from fastapi import APIRouter, HTTPException, UploadFile, File
import uuid

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = None):
    """Upload file endpoint - to be fully implemented in Phase 6."""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_id = str(uuid.uuid4())
    return {
        "file_id": file_id,
        "filename": file.filename,
        "status": "pending",
    }