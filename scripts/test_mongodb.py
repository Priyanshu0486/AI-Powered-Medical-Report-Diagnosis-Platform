#!/usr/bin/env python3
"""Quick MongoDB Connection Test"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

load_dotenv()

print("🔍 Testing MongoDB Connection...")
print("=" * 60)

try:
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "MedicalRag")
    
    print(f"📍 URI: {mongo_uri[:30]}...{mongo_uri[-30:]}")
    print(f"📁 Database: {db_name}")
    print(f"🔄 Connecting...\n")
    
    # Connect with timeout
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ Connection successful!")
    
    # Get database info
    db = client[db_name]
    collections = db.list_collection_names()
    
    # Get stats
    stats = db.command("dbStats")
    size_mb = stats.get('dataSize', 0) / (1024 * 1024)
    objects = stats.get('objects', 0)
    
    print("\n📊 Database Information:")
    print(f"   Collections: {len(collections)}")
    print(f"   Documents: {objects}")
    print(f"   Size: {size_mb:.2f} MB")
    
    if collections:
        print(f"\n📋 Collections Found:")
        for coll_name in collections:
            coll = db[coll_name]
            count = coll.count_documents({})
            print(f"   • {coll_name}: {count} documents")
    else:
        print(f"\n⚠️  No collections found (database is empty)")
        print(f"   💡 Run: python seed_schemas.py --action create")
        print(f"   💡 Then: python migrate_db.py --action init")
    
    client.close()
    print("\n" + "=" * 60)
    print("🎉 MongoDB is working correctly!")
    
except OperationFailure as e:
    print("❌ Authentication Failed!")
    print(f"   Error: {str(e)}")
    print(f"\n💡 Solution:")
    print(f"   1. Go to https://cloud.mongodb.com")
    print(f"   2. Database Access → Edit User → Reset Password")
    print(f"   3. Update .env with new password")
    
except ConnectionFailure:
    print("❌ Cannot reach MongoDB server")
    print(f"\n💡 Check:")
    print(f"   1. Internet connection")
    print(f"   2. MongoDB URI is correct")
    
except ServerSelectionTimeoutError:
    print("❌ Connection timeout")
    print(f"\n💡 Check:")
    print(f"   1. Network Access in MongoDB Atlas")
    print(f"   2. IP address is whitelisted (0.0.0.0/0)")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
