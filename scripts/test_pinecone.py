#!/usr/bin/env python3
"""
Test Pinecone connection and vector format
"""

import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def test_pinecone_connection():
    """Test Pinecone connection and vector operations"""
    
    # Get environment variables
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rbac-diagnosis-index")
    
    if not PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY not found in environment variables")
        return False
    
    try:
        print("🔍 Testing Pinecone Connection...")
        print(f"📍 Index: {PINECONE_INDEX_NAME}")
        print(f"🔑 API Key: {PINECONE_API_KEY[:10]}...{PINECONE_API_KEY[-4:]}")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"📋 Available indexes: {[idx['name'] for idx in indexes]}")
        
        # Check if our index exists
        if PINECONE_INDEX_NAME not in [idx['name'] for idx in indexes]:
            print(f"❌ Index '{PINECONE_INDEX_NAME}' not found")
            return False
        
        # Get index
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"📊 Index stats:")
        print(f"   Dimension: {stats.dimension}")
        print(f"   Total vectors: {stats.total_vector_count}")
        print(f"   Namespaces: {list(stats.namespaces.keys()) if stats.namespaces else ['default']}")
        
        # Test embeddings
        print("\n🔄 Testing HuggingFace embeddings...")
        embed_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Generate test embedding
        test_text = ["This is a test document for medical diagnosis."]
        embedding = embed_model.embed_documents(test_text)[0]
        print(f"✅ Generated embedding: dimension {len(embedding)}")
        
        # Check if dimensions match
        if len(embedding) != stats.dimension:
            print(f"❌ Dimension mismatch! Embedding: {len(embedding)}, Index: {stats.dimension}")
            return False
        
        # Test vector format
        test_vector = {
            "id": "test-vector-001",
            "values": embedding,
            "metadata": {
                "source": "test.pdf",
                "doc_id": "test-doc",
                "uploader": "test-user",
                "text": "Test medical document content"
            }
        }
        
        print("\n🔄 Testing vector upsert...")
        response = index.upsert(vectors=[test_vector])
        print(f"✅ Test upsert successful: {response.upserted_count} vectors")
        
        # Clean up test vector
        index.delete(ids=["test-vector-001"])
        print("🧹 Cleaned up test vector")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    print("🔍 Pinecone Connection & Vector Format Test")
    print("=" * 50)
    
    success = test_pinecone_connection()
    
    if success:
        print("\n✅ All Pinecone tests passed!")
        print("🎉 Your vectorstore should work correctly now.")
    else:
        print("\n❌ Pinecone tests failed!")
        print("🔧 Check your Pinecone configuration and API key.")

if __name__ == "__main__":
    main()