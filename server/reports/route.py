"""
Enhanced reports route with Cloudinary integration
Supports both cloud (Cloudinary) and local storage options
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from ..auth.route import authenticate
from .vectorstore import load_vectorstore
import uuid
import os
from typing import List, Optional
from ..config.db import reports_collection

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/upload")
async def upload_reports(
    user=Depends(authenticate),
    files: List[UploadFile] = File(...),
    use_cloudinary: Optional[bool] = Query(
        default=None,
        description="Force use of Cloudinary (true) or local storage (false). If not specified, auto-detects based on configuration."
    )
):
    """
    Upload medical reports with support for both Cloudinary and local storage
    
    - **files**: List of medical report files (PDF, TXT)
    - **use_cloudinary**: Optional parameter to force storage method
    """
    if user["role"] != "patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can upload reports for diagnosis"
        )
    
    # Validate file types
    allowed_types = ["application/pdf", "text/plain"]
    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported. Only PDF and TXT files are allowed."
            )
    
    # Validate file sizes (max 10MB per file)
    max_size = 10 * 1024 * 1024  # 10MB
    for file in files:
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is too large. Maximum size is 10MB."
            )
    
    doc_id = str(uuid.uuid4())
    
    try:
        # Determine storage method
        cloudinary_configured = all([
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET")
        ])
        
        if use_cloudinary is True and not cloudinary_configured:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary is not properly configured"
            )
        
        # Process upload
        await load_vectorstore(files, uploaded=user["username"], doc_id=doc_id)
        
        storage_type = "cloudinary" if (use_cloudinary or cloudinary_configured) else "local"
        
        return {
            "message": "Reports uploaded and indexed successfully",
            "doc_id": doc_id,
            "storage_type": storage_type,
            "files_processed": len(files),
            "filenames": [file.filename for file in files]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload processing failed: {str(e)}"
        )


@router.get("/list")
async def list_user_reports(user=Depends(authenticate)):
    """
    List all reports uploaded by the authenticated user
    """
    try:
        # Get reports from MongoDB
        reports = list(reports_collection.find(
            {"uploader": user["username"]},
            {"_id": 0}  # Exclude MongoDB ObjectId
        ))
        
        return {
            "reports": reports,
            "total_reports": len(reports)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve reports: {str(e)}"
        )


@router.get("/storage-status")
async def get_storage_status():
    """
    Get information about current storage configuration
    """
    cloudinary_configured = all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET")
    ])
    
    local_dir = os.getenv("UPLOAD_DIR", "./uploaded_reports")
    local_available = os.path.exists(local_dir)
    
    return {
        "cloudinary": {
            "configured": cloudinary_configured,
            "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME") if cloudinary_configured else None
        },
        "local_storage": {
            "available": local_available,
            "upload_dir": local_dir
        },
        "default_storage": "cloudinary" if cloudinary_configured else "local"
    }