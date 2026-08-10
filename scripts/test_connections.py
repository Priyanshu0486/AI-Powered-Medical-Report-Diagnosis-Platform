#!/usr/bin/env python3
"""
Service Connection Test Script
Tests connections to all external services used by the Medical Diagnosis System
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(service, status, message="", details=""):
    """Print formatted test result"""
    icon = "✅" if status else "❌"
    print(f"\n{icon} {service}")
    if message:
        print(f"   {message}")
    if details:
        print(f"   {details}")

def test_mongodb():
    """Test MongoDB connection"""
    print_header("Testing MongoDB Connection")
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
        
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME", "MedicalRag")
        
        if not mongo_uri:
            print_result("MongoDB", False, "MONGO_URI not found in .env file")
            return False
        
        print(f"📍 Connection URI: {mongo_uri[:30]}...{mongo_uri[-20:]}")
        print(f"📁 Database Name: {db_name}")
        print("🔄 Connecting...")
        
        # Connect with timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        # Get database info
        db = client[db_name]
        collections = db.list_collection_names()
        
        # Get database stats
        stats = db.command("dbStats")
        
        print_result(
            "MongoDB", 
            True, 
            f"Successfully connected to {db_name}",
            f"Collections: {len(collections)} | Size: {stats.get('dataSize', 0) / 1024:.2f} KB"
        )
        
        if collections:
            print(f"   📋 Collections: {', '.join(collections[:5])}")
            if len(collections) > 5:
                print(f"      ... and {len(collections) - 5} more")
        else:
            print("   ⚠️  No collections found (database is empty)")
        
        client.close()
        return True
        
    except ConnectionFailure:
        print_result("MongoDB", False, "Connection failed - Cannot reach MongoDB server")
        return False
    except ServerSelectionTimeoutError:
        print_result("MongoDB", False, "Connection timeout - Check your internet connection")
        return False
    except Exception as e:
        print_result("MongoDB", False, f"Error: {str(e)}")
        return False

def test_google_ai():
    """Test Google AI (Gemini) connection"""
    print_header("Testing Google AI (Gemini) Connection")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print_result("Google AI", False, "GOOGLE_API_KEY not found in .env file")
            return False
        
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
        print("🔄 Testing API...")
        
        # Configure and test
        genai.configure(api_key=api_key)
        
        # List available models
        try:
            models = list(genai.list_models())
        except:
            models = []
        
        # Try a simple generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        
        print_result(
            "Google AI", 
            True, 
            "Successfully connected to Google AI",
            f"Available models: {len(models)} | Test generation: Success"
        )
        
        return True
        
    except ImportError:
        print_result("Google AI", False, "google-generativeai package not installed")
        print("   💡 Install: pip install google-generativeai")
        return False
    except Exception as e:
        print_result("Google AI", False, f"Error: {str(e)}")
        return False

def test_pinecone():
    """Test Pinecone connection"""
    print_header("Testing Pinecone Connection")
    
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not api_key:
            print_result("Pinecone", False, "PINECONE_API_KEY not found in .env file")
            return False
        
        if not index_name:
            print_result("Pinecone", False, "PINECONE_INDEX_NAME not found in .env file")
            return False
        
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
        print(f"📊 Index Name: {index_name}")
        print("🔄 Connecting...")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # List indexes
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        
        if index_name not in index_names:
            print_result(
                "Pinecone", 
                False, 
                f"Index '{index_name}' not found",
                f"Available indexes: {', '.join(index_names) if index_names else 'None'}"
            )
            return False
        
        # Connect to specific index
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        
        print_result(
            "Pinecone", 
            True, 
            f"Successfully connected to index '{index_name}'",
            f"Total vectors: {stats.get('total_vector_count', 0)} | Dimension: {stats.get('dimension', 'N/A')}"
        )
        
        return True
        
    except ImportError:
        print_result("Pinecone", False, "pinecone package not installed")
        print("   💡 Install: pip install pinecone-client")
        return False
    except Exception as e:
        print_result("Pinecone", False, f"Error: {str(e)}")
        return False

def test_groq():
    """Test Groq AI connection"""
    print_header("Testing Groq AI Connection")
    
    try:
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            print_result("Groq AI", False, "GROQ_API_KEY not found in .env file")
            return False
        
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
        print("🔄 Testing API...")
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Try a simple completion
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.3-70b-versatile",
            max_tokens=10
        )
        
        print_result(
            "Groq AI", 
            True, 
            "Successfully connected to Groq AI",
            f"Test completion: Success | Model: llama-3.3-70b-versatile"
        )
        
        return True
        
    except ImportError:
        print_result("Groq AI", False, "groq package not installed")
        print("   💡 Install: pip install groq")
        return False
    except Exception as e:
        print_result("Groq AI", False, f"Error: {str(e)}")
        return False

def test_upload_directory():
    """Test upload directory configuration"""
    print_header("Testing Upload Directory")
    
    try:
        upload_dir = os.getenv("UPLOAD_DIR", "./uploaded_reports")
        
        print(f"📁 Upload Directory: {upload_dir}")
        
        # Check if directory exists
        if os.path.exists(upload_dir):
            # Count files
            files = os.listdir(upload_dir)
            total_size = sum(
                os.path.getsize(os.path.join(upload_dir, f)) 
                for f in files 
                if os.path.isfile(os.path.join(upload_dir, f))
            )
            
            print_result(
                "Upload Directory", 
                True, 
                f"Directory exists and is accessible",
                f"Files: {len(files)} | Total size: {total_size / 1024:.2f} KB"
            )
        else:
            print_result(
                "Upload Directory", 
                True, 
                "Directory does not exist (will be created when needed)"
            )
        
        return True
        
    except Exception as e:
        print_result("Upload Directory", False, f"Error: {str(e)}")
        return False

def test_api_server():
    """Test if API server is running"""
    print_header("Testing API Server")
    
    try:
        import requests
        
        api_url = os.getenv("API_URL", "http://localhost:8000")
        
        print(f"🌐 API URL: {api_url}")
        print("🔄 Checking server...")
        
        # Try to connect to the server
        response = requests.get(f"{api_url}/", timeout=3)
        
        if response.status_code == 200:
            print_result(
                "API Server", 
                True, 
                f"Server is running on {api_url}",
                f"Status: {response.status_code} OK"
            )
            return True
        else:
            print_result(
                "API Server", 
                False, 
                f"Server responded with status {response.status_code}"
            )
            return False
        
    except ImportError:
        print_result("API Server", False, "requests package not installed")
        print("   💡 Install: pip install requests")
        return False
    except requests.exceptions.ConnectionError:
        print_result(
            "API Server", 
            False, 
            "Server is not running",
            "💡 Start server: uvicorn server.main:app --reload"
        )
        return False
    except requests.exceptions.Timeout:
        print_result("API Server", False, "Connection timeout")
        return False
    except Exception as e:
        print_result("API Server", False, f"Error: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("\n" + "🔍" * 30)
    print("   SERVICE CONNECTION TEST")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍" * 30)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("\n❌ Error: .env file not found!")
        print("   Please create .env file with required configuration")
        sys.exit(1)
    
    print("\n✅ Found .env file")
    
    # Run all tests
    results = {
        "MongoDB": test_mongodb(),
        "Google AI": test_google_ai(),
        "Pinecone": test_pinecone(),
        "Groq AI": test_groq(),
        "Upload Directory": test_upload_directory(),
        "API Server": test_api_server()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
    
    print("\n" + "-" * 60)
    print(f"Result: {passed}/{total} services connected successfully")
    print("-" * 60)
    
    if passed == total:
        print("\n🎉 All services are operational!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} service(s) need attention")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🚫 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
