#!/usr/bin/env python3
"""
Quick test for the MongoDB SSL fix
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import ssl
import certifi

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "MedicalRag")

print("🔍 Testing MongoDB SSL Connection Fix...")
print("=" * 60)

if not MONGO_URI:
    print("❌ MONGO_URI not found in environment variables")
    print("💡 Create a .env file with MONGO_URI=your_mongodb_connection_string")
    exit(1)

try:
    print(f"📍 Testing connection to: {MONGO_URI[:30]}...{MONGO_URI[-15:]}")
    
    # Test with the new SSL configuration
    client_options = {
        'serverSelectionTimeoutMS': 30000,
        'connectTimeoutMS': 30000,
        'socketTimeoutMS': 30000,
        'maxPoolSize': 50,
        'retryWrites': True,
        'w': 'majority'
    }
    
    # Add TLS configuration for Atlas
    if 'mongodb+srv://' in MONGO_URI:
        client_options.update({
            'tls': True,
            'tlsAllowInvalidCertificates': True,
            'tlsAllowInvalidHostnames': True
        })
        print("🔐 Using TLS configuration for MongoDB Atlas")
    
    # Create client and test connection
    print("🔄 Connecting...")
    client = MongoClient(MONGO_URI, **client_options)
    
    # Test the connection
    client.admin.command('ping')
    print("✅ Connection successful!")
    
    # Get database info
    db = client[DB_NAME]
    collections = db.list_collection_names()
    
    print(f"\n📊 Database: {DB_NAME}")
    print(f"📋 Collections found: {len(collections)}")
    
    if collections:
        for coll_name in collections:
            count = db[coll_name].count_documents({})
            print(f"   • {coll_name}: {count} documents")
    else:
        print("   (No collections found - database is empty)")
    
    client.close()
    print("\n✅ SSL connection fix working correctly!")
    
except ServerSelectionTimeoutError as e:
    print(f"❌ Connection timeout: {e}")
    print("\n💡 Possible solutions:")
    print("   1. Check your internet connection")
    print("   2. Verify MongoDB Atlas network access (whitelist 0.0.0.0/0)")
    print("   3. Check if your firewall is blocking the connection")
    
except ConnectionFailure as e:
    print(f"❌ Connection failed: {e}")
    print("\n💡 Check:")
    print("   1. MongoDB URI is correct")
    print("   2. Username and password are correct")
    print("   3. Database user has proper permissions")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"   Error type: {type(e).__name__}")
    
    # Try a simple fallback connection
    print("\n🔄 Trying fallback connection...")
    try:
        simple_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        simple_client.admin.command('ping')
        print("✅ Fallback connection successful!")
        simple_client.close()
    except Exception as fallback_e:
        print(f"❌ Fallback also failed: {fallback_e}")

print("\n" + "=" * 60)