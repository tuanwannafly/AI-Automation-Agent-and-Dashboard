import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
from ..models.schemas import LLMProvider
from ..core.config import settings

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
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "fileId": file_id,
                "filename": file.filename,
                "size": file_size,
                "status": "uploaded",
                "type": ext,
                "uploadedAt": datetime.now().timestamp()
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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
    for ext in ["pdf", "docx"]:
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
            return JSONResponse(content={"success": True})
    
    raise HTTPException(status_code=404, detail="File not found")