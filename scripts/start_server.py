#!/usr/bin/env python3
"""
Production startup script for Render deployment
Handles initialization and warming up of services
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def warm_up_services():
    """Warm up services to reduce cold start time"""
    try:
        logger.info("🚀 Starting Medical Diagnosis API...")
        
        # Test MongoDB connection
        try:
            from server.config.db import create_mongo_client
            client = create_mongo_client()
            client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
        
        # Test Pinecone connection
        try:
            import pinecone
            pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))
            logger.info("✅ Pinecone connection successful")
        except Exception as e:
            logger.error(f"❌ Pinecone connection failed: {e}")
        
        # Pre-load embeddings model
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embed_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            # Warm up model with a test embedding
            test_embedding = embed_model.embed_query("test")
            logger.info("✅ Embeddings model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Embeddings model loading failed: {e}")
        
        logger.info("🎉 Service warm-up completed!")
        
    except Exception as e:
        logger.error(f"💥 Service warm-up failed: {e}")

def main():
    """Main startup function"""
    logger.info("🏥 Medical Diagnosis API - Production Startup")
    logger.info(f"📅 Startup Time: {datetime.utcnow().isoformat()}")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🐍 Python Version: {sys.version}")
    
    # Run warm-up
    asyncio.run(warm_up_services())
    
    # Start the FastAPI server
    import uvicorn
    
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🚀 Starting server on port {port}")
    
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        reload=False  # Never use reload in production
    )

if __name__ == "__main__":
    main()