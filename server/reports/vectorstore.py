import os
import time
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Using HuggingFace embeddings (free, unlimited, no API key needed)
from langchain_huggingface import HuggingFaceEmbeddings
# Alternative: from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ..config.db import reports_collection
from typing import List
from fastapi import UploadFile

# Cloudinary support - import only if available
try:
    from .cloudinary_service import cloudinary_service
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rbac-diagnosis-index")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_reports")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.makedirs(UPLOAD_DIR, exist_ok=True)

# initialize pinecone
pc=Pinecone(api_key=PINECONE_API_KEY)
spec=ServerlessSpec(cloud="aws",region=PINECONE_ENV)
existing_indexes=[i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    # Dimension 384 for HuggingFace all-MiniLM-L6-v2 (was 768 for Google embeddings)
    pc.create_index(name=PINECONE_INDEX_NAME,dimension=384,metric="cosine",spec=spec)
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index=pc.Index(PINECONE_INDEX_NAME)


async def load_vectorstore(uploaded_files: List[UploadFile], uploaded: str, doc_id: str):
    """
    Smart function that auto-detects storage method and processes files accordingly
    """
    # Check if Cloudinary is configured
    cloudinary_configured = all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"), 
        os.getenv("CLOUDINARY_API_SECRET")
    ]) and CLOUDINARY_AVAILABLE
    
    if cloudinary_configured:
        print("🌩️  Cloudinary configured - using cloud storage")
        await load_vectorstore_with_cloudinary(uploaded_files, uploaded, doc_id)
    else:
        print("📁 Cloudinary not configured - using local storage")
        await load_vectorstore_local(uploaded_files, uploaded, doc_id)


async def load_vectorstore_with_cloudinary(uploaded_files: List[UploadFile], uploaded: str, doc_id: str):
    """
    Save files to Cloudinary, process them for embeddings, and store in Pinecone
    """
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    cloudinary_urls = []
    all_chunks = []
    
    for file in uploaded_files:
        try:
            print(f"📤 Uploading {file.filename} to Cloudinary...")
            
            # Upload to Cloudinary
            upload_result = await cloudinary_service.upload_document(file, doc_id, uploaded)
            cloudinary_urls.append({
                "filename": file.filename,
                "cloudinary_url": upload_result["cloudinary_url"],
                "cloudinary_public_id": upload_result["cloudinary_public_id"],
                "size": upload_result["bytes"]
            })
            
            print(f"✅ Uploaded to Cloudinary: {upload_result['cloudinary_url']}")
            
            # Download file from Cloudinary for processing
            print(f"📥 Downloading {file.filename} from Cloudinary for processing...")
            file_content = await cloudinary_service.download_document(
                upload_result["cloudinary_public_id"]
            )
            
            # Create temporary file for PDF processing
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                file_content.seek(0)
                temp_file.write(file_content.read())
                temp_file_path = temp_file.name
            
            try:
                # Load PDF pages
                loader = PyPDFLoader(temp_file_path)
                documents = loader.load()
                
                # Split into chunks
                splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
                chunks = splitter.split_documents(documents)
                
                # Add file metadata to chunks
                for chunk in chunks:
                    chunk.metadata.update({
                        "source": file.filename,
                        "cloudinary_url": upload_result["cloudinary_url"],
                        "cloudinary_public_id": upload_result["cloudinary_public_id"]
                    })
                
                all_chunks.extend(chunks)
                print(f"📄 Processed {len(chunks)} chunks from {file.filename}")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"❌ Error processing {file.filename}: {str(e)}")
            raise
    
    # Process embeddings and store
    await _process_chunks_and_store(all_chunks, doc_id, uploaded, embed_model, cloudinary_urls=cloudinary_urls)


async def load_vectorstore_local(uploaded_files: List[UploadFile], uploaded: str, doc_id: str):
    """
    Original local storage implementation
    """
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    all_chunks = []
    filenames = []
    
    for file in uploaded_files:
        filename = Path(file.filename).name
        filenames.append(filename)
        save_path = Path(UPLOAD_DIR) / f"{doc_id}_{filename}"
        content = await file.read()
        
        with open(save_path, "wb") as f:
            f.write(content)
        
        # Load PDF pages
        loader = PyPDFLoader(str(save_path))
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        
        # Add source metadata
        for chunk in chunks:
            chunk.metadata["source"] = filename
            
        all_chunks.extend(chunks)
    
    # Process embeddings and store
    await _process_chunks_and_store(all_chunks, doc_id, uploaded, embed_model, local_filenames=filenames)


async def _process_chunks_and_store(all_chunks, doc_id, uploaded, embed_model, cloudinary_urls=None, local_filenames=None):
    """
    Common function to process chunks and store in Pinecone and MongoDB
    """
    if not all_chunks:
        raise ValueError("No chunks were created from the uploaded files")
    
    texts = [chunk.page_content for chunk in all_chunks]
    ids = [f"{doc_id}-{i}" for i in range(len(all_chunks))]
    metadatas = []
    
    for i, chunk in enumerate(all_chunks):
        metadata = {
            "source": chunk.metadata.get("source"),
            "doc_id": doc_id,
            "uploader": uploaded,
            "page": chunk.metadata.get("page", None),
            "text": chunk.page_content[:2000]
        }
        
        # Add Cloudinary-specific metadata if available
        if cloudinary_urls:
            metadata.update({
                "cloudinary_url": chunk.metadata.get("cloudinary_url"),
                "cloudinary_public_id": chunk.metadata.get("cloudinary_public_id")
            })
        
        metadatas.append(metadata)
    
    # Generate embeddings
    print(f"🔄 Generating embeddings for {len(texts)} text chunks...")
    embeddings = await asyncio.to_thread(embed_model.embed_documents, texts)
    
    # Validate embeddings
    if not embeddings or len(embeddings) != len(texts):
        raise ValueError(f"Embeddings generation failed. Expected {len(texts)}, got {len(embeddings)}")
    
    print(f"✅ Generated {len(embeddings)} embeddings (dimension: {len(embeddings[0]) if embeddings else 'unknown'})")
    
    # Prepare vectors for Pinecone
    vectors = [
        {
            "id": ids[i],
            "values": embeddings[i],
            "metadata": metadatas[i]
        }
        for i in range(len(ids))
    ]
    
    # Upsert to Pinecone
    def upsert():
        try:
            print(f"📊 Upserting {len(vectors)} vectors to Pinecone index '{PINECONE_INDEX_NAME}'")
            response = index.upsert(vectors=vectors)
            print(f"✅ Successfully upserted {response.upserted_count} vectors")
            return response
        except Exception as e:
            print(f"❌ Pinecone upsert failed: {e}")
            raise
    
    await asyncio.to_thread(upsert)
    
    # Save report metadata in MongoDB
    if cloudinary_urls:
        # Cloudinary storage
        primary_filename = cloudinary_urls[0]["filename"] if cloudinary_urls else "multiple_files"
        
        reports_collection.insert_one({
            "doc_id": doc_id,
            "filename": primary_filename,  # Required field for backward compatibility
            "files": cloudinary_urls,  # Store Cloudinary URLs (new field for multiple files)
            "uploader": uploaded,
            "num_chunks": len(all_chunks),
            "uploaded_at": time.time(),
            "storage_type": "cloudinary"  # Flag to indicate storage method
        })
    else:
        # Local storage
        primary_filename = local_filenames[0] if local_filenames else "unknown"
        
        reports_collection.insert_one({
            "doc_id": doc_id,
            "filename": primary_filename,
            "uploader": uploaded,
            "num_chunks": len(all_chunks),
            "uploaded_at": time.time(),
            "storage_type": "local"
        })
    
    print(f"✅ Successfully processed {len(uploaded_files)} files with {len(all_chunks)} total chunks")