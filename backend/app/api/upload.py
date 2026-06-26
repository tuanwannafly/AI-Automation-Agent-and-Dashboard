from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_processor import FileProcessor
from app.services.qdrant_client import index_document
import uuid, os, aiofiles

router = APIRouter()
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file, extract text, and index into Qdrant."""
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")

    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"

    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    processor = FileProcessor()
    text = await processor.extract_text(file_path, file.content_type)

    await index_document(file_id=file_id, text=text, source=file.filename)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "text_length": len(text),
        "status": "indexed",
    }