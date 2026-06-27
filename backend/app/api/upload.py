import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
from ..models.schemas import LLMProvider
from ..core.config import settings
from ..services.rag import rag_engine

router = APIRouter()

UPLOAD_DIR = settings.UPLOADS_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    
    file_id = f"file_{uuid4()}"
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        text_content = await extract_text(file_path, ext)
        if text_content:
            rag_engine.index_file(file_id, text_content, {"filename": file.filename, "type": ext})
            status = "indexed"
        else:
            status = "uploaded"
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "id": file_id,
                "fileId": file_id,
                "filename": file.filename,
                "size": file_size,
                "status": status,
                "type": ext,
                "uploadedAt": datetime.now().timestamp()
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def extract_text(file_path: str, ext: str) -> str:
    try:
        if ext == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext == "docx":
            from docx import Document
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception as e:
        print(f"Text extraction error: {e}")
    return ""

@router.get("/uploads")
async def list_uploads():
    files = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                ext = filename.split(".")[-1]
                file_id = filename.replace(f".{ext}", "")
                files.append({
                    "id": file_id,
                    "fileId": file_id,
                    "filename": filename,
                    "size": stat.st_size,
                    "type": ext,
                    "status": "indexed",
                    "uploadedAt": stat.st_mtime
                })
    
    return JSONResponse(content={
        "success": True,
        "data": {"files": files}
    })

@router.delete("/uploads/{file_id}")
async def delete_upload(file_id: str):
    deleted_from_disk = False
    for ext in ["pdf", "docx"]:
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_from_disk = True
    
    if deleted_from_disk:
        rag_engine.delete_file(file_id)
        return JSONResponse(content={"success": True})
    
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/rag/search")
async def search_rag(query: str, limit: int = 5):
    results = rag_engine.query(query, limit)
    return JSONResponse(content={
        "success": True,
        "data": {"results": results, "query": query}
    })

@router.get("/rag/files")
async def list_indexed_files():
    files = rag_engine.get_indexed_files()
    return JSONResponse(content={
        "success": True,
        "data": {"files": files}
    })