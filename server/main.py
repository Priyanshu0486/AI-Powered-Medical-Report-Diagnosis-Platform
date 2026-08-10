from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .auth.route import router as auth_router
from .reports.route import router as report_router
from .diagnosis.route import router as diagnosis_router
from .config.db import client, db
import os
from datetime import datetime
from pinecone import Pinecone

app = FastAPI(
    title="Medical Report Diagnosis API",
    description="AI-powered medical report diagnosis system with FastAPI backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Production CORS configuration
allowed_origins = [
    "http://localhost:8501",  # Local Streamlit development
    "https://*.streamlit.app",  # Streamlit Cloud apps
    "https://*.streamlitapp.com",  # Streamlit Cloud apps (old domain)
    "http://localhost:3000",  # Local React development (if needed)
]

# Add environment-specific origins
if os.getenv("ENVIRONMENT") == "production":
    # Add your production frontend URLs
    allowed_origins.extend([
        "https://your-streamlit-app.streamlit.app",  # Replace with actual URL
        "https://medical-diagnosis.streamlit.app",   # Example
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Health check endpoints for Render monitoring
@app.get("/health")
async def health_check():
    """Basic health check endpoint for Render health checks"""
    return {
        "status": "healthy",
        "service": "Medical Report Diagnosis API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health/db")
async def database_health_check():
    """Database connectivity health check"""
    try:
        if client is None:
            raise HTTPException(status_code=503, detail="Database client not initialized")
        
        # Test MongoDB connection
        client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "type": "MongoDB"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database health check failed: {str(e)}"
        )

@app.get("/health/pinecone")
async def pinecone_health_check():
    """Pinecone vector database health check"""
    try:
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rbac-diagnosis-index")
        
        if not PINECONE_API_KEY:
            raise HTTPException(status_code=503, detail="Pinecone API key not configured")
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        indexes = pc.list_indexes()
        
        return {
            "status": "healthy",
            "vector_database": "connected",
            "type": "Pinecone",
            "available_indexes": [idx['name'] for idx in indexes],
            "target_index": PINECONE_INDEX_NAME
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Pinecone health check failed: {str(e)}"
        )

app.include_router(auth_router)
app.include_router(report_router)
app.include_router(diagnosis_router)