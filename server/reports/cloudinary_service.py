"""
Cloudinary integration for Medical Report file uploads
Handles secure document upload, storage, and retrieval from Cloudinary
"""

import os
import tempfile
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import requests
from io import BytesIO

load_dotenv()

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")  
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

class CloudinaryService:
    """Service for handling document uploads to Cloudinary"""
    
    def __init__(self):
        self.folder_name = "medical_reports"
        
    async def upload_document(self, file: UploadFile, doc_id: str, uploader: str) -> Dict[str, Any]:
        """
        Upload document to Cloudinary with metadata
        
        Args:
            file: FastAPI UploadFile object
            doc_id: Unique document identifier
            uploader: Username of the uploader
            
        Returns:
            Dict containing upload result with URL and metadata
        """
        try:
            # Read file content
            content = await file.read()
            
            # Generate unique public_id
            filename = Path(file.filename).stem
            public_id = f"{self.folder_name}/{doc_id}_{filename}"
            
            # Upload to Cloudinary
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                content,
                public_id=public_id,
                folder=self.folder_name,
                resource_type="raw",  # For non-image files (PDFs, TXT, etc.)
                context={
                    "doc_id": doc_id,
                    "uploader": uploader,
                    "original_filename": file.filename,
                    "content_type": file.content_type
                },
                tags=[doc_id, uploader, "medical_report"],
                # Optional: Add access control
                # access_mode="authenticated"  # Requires signed URLs for access
            )
            
            return {
                "success": True,
                "cloudinary_url": upload_result.get("secure_url"),
                "cloudinary_public_id": upload_result.get("public_id"),
                "resource_type": upload_result.get("resource_type"),
                "format": upload_result.get("format"),
                "bytes": upload_result.get("bytes"),
                "original_filename": file.filename,
                "upload_timestamp": upload_result.get("created_at")
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cloudinary upload failed: {str(e)}"
            )
    
    async def download_document(self, cloudinary_public_id: str) -> BytesIO:
        """
        Download document from Cloudinary for processing
        
        Args:
            cloudinary_public_id: Cloudinary public ID of the document
            
        Returns:
            BytesIO object containing the file content
        """
        try:
            # Get the secure URL
            url_result = cloudinary.utils.cloudinary_url(
                cloudinary_public_id,
                resource_type="raw",
                secure=True
            )
            
            download_url = url_result[0]
            
            # Download the file
            response = await asyncio.to_thread(requests.get, download_url)
            response.raise_for_status()
            
            return BytesIO(response.content)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download from Cloudinary: {str(e)}"
            )
    
    async def get_signed_url(self, cloudinary_public_id: str, expiry_seconds: int = 3600) -> str:
        """
        Generate signed URL for secure document access
        
        Args:
            cloudinary_public_id: Cloudinary public ID
            expiry_seconds: URL expiry time in seconds
            
        Returns:
            Signed URL for secure access
        """
        try:
            # Generate signed URL
            signed_url = cloudinary.utils.cloudinary_url(
                cloudinary_public_id,
                resource_type="raw",
                secure=True,
                sign_url=True,
                expires_at=int(asyncio.get_event_loop().time()) + expiry_seconds
            )[0]
            
            return signed_url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate signed URL: {str(e)}"
            )
    
    async def delete_document(self, cloudinary_public_id: str) -> bool:
        """
        Delete document from Cloudinary
        
        Args:
            cloudinary_public_id: Cloudinary public ID
            
        Returns:
            True if deletion successful
        """
        try:
            result = await asyncio.to_thread(
                cloudinary.uploader.destroy,
                cloudinary_public_id,
                resource_type="raw"
            )
            
            return result.get("result") == "ok"
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete from Cloudinary: {str(e)}"
            )
    
    async def list_documents(self, uploader: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List documents uploaded by a user
        
        Args:
            uploader: Filter by uploader username
            
        Returns:
            List of document metadata
        """
        try:
            # Search parameters
            expression = f"folder:{self.folder_name}"
            if uploader:
                expression += f" AND context.uploader:{uploader}"
            
            result = await asyncio.to_thread(
                cloudinary.api.resources,
                resource_type="raw",
                context=True,
                tags=True,
                max_results=100
            )
            
            documents = []
            for resource in result.get("resources", []):
                context = resource.get("context", {})
                if uploader and context.get("uploader") != uploader:
                    continue
                    
                documents.append({
                    "public_id": resource["public_id"],
                    "url": resource["secure_url"],
                    "doc_id": context.get("doc_id"),
                    "uploader": context.get("uploader"),
                    "filename": context.get("original_filename"),
                    "size": resource.get("bytes"),
                    "uploaded_at": resource.get("created_at"),
                    "tags": resource.get("tags", [])
                })
            
            return documents
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list documents: {str(e)}"
            )

# Create service instance
cloudinary_service = CloudinaryService()