#!/usr/bin/env python3
"""
MongoDB Atlas SSL Connection Diagnostics and Fix
Comprehensive solution for SSL handshake issues
"""

import os
import sys
import ssl
import certifi
import platform
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "MedicalRag")

def print_system_info():
    """Print system information for debugging"""
    print("🖥️  System Information:")
    print(f"   Python: {sys.version}")
    print(f"   Platform: {platform.platform()}")
    print(f"   SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"   Certifi path: {certifi.where()}")
    print()

def test_connection_method(method_name, client_options):
    """Test a specific connection method"""
    try:
        print(f"🔄 Testing {method_name}...")
        client = MongoClient(MONGO_URI, **client_options)
        client.admin.command('ping')
        
        # Test database operations
        db = client[DB_NAME]
        collections = db.list_collection_names()
        
        print(f"   ✅ {method_name} - SUCCESS!")
        print(f"   📊 Database: {DB_NAME} ({len(collections)} collections)")
        
        client.close()
        return True, client_options
        
    except Exception as e:
        print(f"   ❌ {method_name} - Failed: {str(e)[:100]}...")
        return False, None

def main():
    print("🔍 MongoDB Atlas SSL Connection Diagnostics")
    print("=" * 60)
    
    if not MONGO_URI:
        print("❌ MONGO_URI not found in environment variables")
        return
    
    print_system_info()
    
    print(f"📍 Testing connection to MongoDB Atlas")
    print(f"   URI: {MONGO_URI[:30]}...{MONGO_URI[-20:]}")
    print()
    
    # Test different connection methods
    connection_methods = [
        # Method 1: Default PyMongo SSL handling
        ("Method 1: Default SSL", {
            'serverSelectionTimeoutMS': 30000,
        }),
        
        # Method 2: Bypass SSL certificate validation
        ("Method 2: Bypass SSL validation", {
            'serverSelectionTimeoutMS': 30000,
            'tls': True,
            'tlsAllowInvalidCertificates': True,
            'tlsAllowInvalidHostnames': True
        }),
        
        # Method 3: Use certifi certificates
        ("Method 3: Use certifi certs", {
            'serverSelectionTimeoutMS': 30000,
            'tls': True,
            'tlsCAFile': certifi.where()
        }),
        
        # Method 4: Minimal options
        ("Method 4: Minimal config", {
            'serverSelectionTimeoutMS': 15000,
            'connectTimeoutMS': 15000,
        }),
        
        # Method 5: Disable SSL entirely (only for troubleshooting)
        ("Method 5: No SSL (troubleshoot)", {
            'serverSelectionTimeoutMS': 30000,
            'tls': False
        })
    ]
    
    working_config = None
    
    for method_name, options in connection_methods:
        success, config = test_connection_method(method_name, options)
        if success and working_config is None:
            working_config = config
            print(f"🎉 Found working configuration: {method_name}")
            break
        print()
    
    if working_config:
        print("✅ SUCCESS! MongoDB connection is working.")
        print("\n📋 Recommended configuration for your db.py:")
        print("-" * 40)
        print("client_options = {")
        for key, value in working_config.items():
            if isinstance(value, str):
                print(f'    "{key}": "{value}",')
            else:
                print(f'    "{key}": {value},')
        print("}")
        print("-" * 40)
        
    else:
        print("❌ All connection methods failed.")
        print("\n🔧 Additional troubleshooting steps:")
        print("1. Check your MongoDB Atlas network access settings")
        print("   - Go to MongoDB Atlas → Network Access")
        print("   - Add IP address 0.0.0.0/0 (allow all) for testing")
        print()
        print("2. Verify your connection string")
        print("   - Username and password are correct")
        print("   - Database name exists")
        print()
        print("3. Check firewall/antivirus settings")
        print("   - Temporarily disable firewall")
        print("   - Check if antivirus is blocking connections")
        print()
        print("4. Try updating your system:")
        print("   - pip install --upgrade pymongo certifi")
        print("   - Update Windows (for SSL/TLS updates)")

if __name__ == "__main__":
    main()