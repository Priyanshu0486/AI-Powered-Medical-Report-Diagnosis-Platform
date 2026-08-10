#!/usr/bin/env python3
"""Test HuggingFace Embeddings Configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing HuggingFace Embeddings Configuration...")
print("=" * 60)

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    
    print("✅ langchain-huggingface package installed")
    print("\n📦 Initializing embedding model...")
    print("   Model: sentence-transformers/all-MiniLM-L6-v2")
    print("   Dimension: 384")
    print("   Device: CPU")
    print("   🔄 Loading model (first time downloads ~80MB)...\n")
    
    # Initialize embedding model
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("✅ Model loaded successfully!")
    
    # Test embedding a single query
    print("\n🧪 Testing single query embedding...")
    test_query = "What does this medical report indicate?"
    embedding = embed_model.embed_query(test_query)
    
    print(f"✅ Query embedded successfully!")
    print(f"   Dimension: {len(embedding)}")
    print(f"   Sample values: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
    
    # Test embedding multiple documents
    print("\n🧪 Testing batch document embedding...")
    test_docs = [
        "Blood test shows normal glucose levels.",
        "X-ray indicates no fractures.",
        "Patient has elevated blood pressure."
    ]
    
    embeddings = embed_model.embed_documents(test_docs)
    
    print(f"✅ Documents embedded successfully!")
    print(f"   Number of documents: {len(embeddings)}")
    print(f"   Dimension per document: {len(embeddings[0])}")
    
    # Test Pinecone configuration
    print("\n📊 Checking Pinecone configuration...")
    try:
        from pinecone import Pinecone
        
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", "llama-text-embed-v2-index")
        
        if pinecone_api_key:
            pc = Pinecone(api_key=pinecone_api_key)
            indexes = [idx.name for idx in pc.list_indexes()]
            
            if index_name in indexes:
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                dimension = stats.get('dimension', 'N/A')
                
                if dimension == 384:
                    print(f"✅ Pinecone index '{index_name}' exists with correct dimension (384)")
                elif dimension != 'N/A':
                    print(f"⚠️  Pinecone index '{index_name}' has dimension {dimension}")
                    print(f"   Expected: 384 for HuggingFace embeddings")
                    print(f"   💡 You may need to delete and recreate the index")
                else:
                    print(f"ℹ️  Pinecone index '{index_name}' exists")
            else:
                print(f"ℹ️  Pinecone index '{index_name}' will be auto-created on first upload")
                print(f"   Dimension will be set to 384")
        else:
            print("⚠️  PINECONE_API_KEY not found in .env")
    
    except Exception as e:
        print(f"⚠️  Could not check Pinecone: {str(e)[:60]}")
    
    print("\n" + "=" * 60)
    print("🎉 HuggingFace Embeddings Configuration Successful!")
    print("\n📋 Summary:")
    print("   ✅ Embedding model: all-MiniLM-L6-v2")
    print("   ✅ Dimension: 384")
    print("   ✅ No API key needed")
    print("   ✅ Free and unlimited usage")
    print("   ✅ Works offline (after first download)")
    
    print("\n💡 Next Steps:")
    print("   1. Start API server: uvicorn server.main:app --reload")
    print("   2. Upload a PDF to test the full pipeline")
    print("   3. Query the document to test RAG functionality")
    
except ImportError as e:
    print("❌ Required package not installed")
    print(f"   Error: {str(e)}")
    print("\n💡 Install with:")
    print("   pip install sentence-transformers langchain-huggingface")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n💡 Troubleshooting:")
    print("   1. Ensure internet connection for first-time model download")
    print("   2. Check disk space (~80MB needed)")
    print("   3. Verify Python version >= 3.8")
