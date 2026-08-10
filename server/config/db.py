from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "MedicalRag")

def create_mongo_client():
    """Create MongoDB client with optimized configuration"""
    try:
        # Optimized MongoDB connection options
        client_options = {
            'serverSelectionTimeoutMS': 30000,  # 30 seconds
            'connectTimeoutMS': 30000,  # 30 seconds  
            'socketTimeoutMS': 30000,   # 30 seconds
            'maxPoolSize': 50,
            'retryWrites': True,
            'w': 'majority'
        }
        
        return MongoClient(MONGO_URI, **client_options)
    
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        raise

# Create client with error handling
try:
    client = create_mongo_client()
    db = client[DB_NAME]
    
    # Test connection immediately  
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
    
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("💡 Note: Ensure PyMongo is updated to latest version (4.15.3+)")
    print("   Run: pip install --upgrade pymongo")
    
    # Create dummy client to prevent import errors
    client = None
    db = None
    
except Exception as e:
    print(f"❌ Unexpected MongoDB error: {e}")
    client = None
    db = None


# Collections (with safety checks)
if db is not None:
    users_collection = db["users"]
    reports_collection = db["reports"]
    diagnosis_collection = db["diagnosis_history"]
else:
    # Create dummy collections to prevent import errors
    class DummyCollection:
        def find_one(self, *args, **kwargs):
            raise ConnectionFailure("MongoDB not connected")
        def insert_one(self, *args, **kwargs):
            raise ConnectionFailure("MongoDB not connected")
        def find(self, *args, **kwargs):
            raise ConnectionFailure("MongoDB not connected")
        def update_one(self, *args, **kwargs):
            raise ConnectionFailure("MongoDB not connected")
        def delete_one(self, *args, **kwargs):
            raise ConnectionFailure("MongoDB not connected")
    
    users_collection = DummyCollection()
    reports_collection = DummyCollection()
    diagnosis_collection = DummyCollection()