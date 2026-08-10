#!/usr/bin/env python3
"""
MongoDB Migration Script for Medical Report Diagnosis System

This script handles database migrations including:
- Database initialization
- Collection creation with proper indexes
- Sample data insertion
- Schema validation
- Migration rollback capabilities

Usage:
    python migrate_db.py --action init          # Initialize database
    python migrate_db.py --action migrate       # Run migrations
    python migrate_db.py --action rollback      # Rollback last migration
    python migrate_db.py --action status        # Check migration status
    python migrate_db.py --action seed          # Seed with sample data
"""

import argparse
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
import os
import hashlib

# Load environment variables
load_dotenv()

class MigrationManager:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "rbac-diagnosis")
        self.client = None
        self.db = None
        self.migration_history = []
        
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.mongo_uri)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print(f"✅ Connected to MongoDB: {self.db_name}")
            return True
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")
    
    def create_migration_collection(self):
        """Create migration tracking collection"""
        if "migrations" not in self.db.list_collection_names():
            self.db.create_collection("migrations")
            print("📋 Created migrations tracking collection")
    
    def get_migration_status(self):
        """Get current migration status"""
        self.create_migration_collection()
        migrations = list(self.db.migrations.find().sort("timestamp", DESCENDING))
        
        print("\n📊 Migration Status:")
        print("-" * 50)
        if not migrations:
            print("No migrations found")
        else:
            for migration in migrations:
                status_icon = "✅" if migration["status"] == "completed" else "❌"
                print(f"{status_icon} {migration['name']} - {migration['timestamp']}")
        print("-" * 50)
        
        return migrations
    
    def record_migration(self, name: str, status: str, description: str = ""):
        """Record migration in tracking collection"""
        migration_record = {
            "name": name,
            "status": status,
            "timestamp": datetime.now(),
            "description": description
        }
        self.db.migrations.insert_one(migration_record)
    
    def init_database(self):
        """Initialize database with collections and indexes"""
        print("🚀 Initializing database...")
        
        try:
            # Create collections if they don't exist
            collections_to_create = [
                "users",
                "reports", 
                "diagnosis_history"
            ]
            
            existing_collections = self.db.list_collection_names()
            
            for collection_name in collections_to_create:
                if collection_name not in existing_collections:
                    self.db.create_collection(collection_name)
                    print(f"📁 Created collection: {collection_name}")
                else:
                    print(f"📁 Collection already exists: {collection_name}")
            
            # Create indexes
            self.create_indexes()
            
            # Record migration
            self.record_migration("database_init", "completed", "Database initialization")
            
            print("✅ Database initialization completed!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            self.record_migration("database_init", "failed", str(e))
            return False
    
    def create_indexes(self):
        """Create database indexes for optimal performance"""
        print("📇 Creating database indexes...")
        
        try:
            # Users collection indexes
            self.db.users.create_index([("username", ASCENDING)], unique=True)
            self.db.users.create_index([("role", ASCENDING)])
            print("  📇 Users indexes created")
            
            # Reports collection indexes
            self.db.reports.create_index([("doc_id", ASCENDING)], unique=True)
            self.db.reports.create_index([("uploader", ASCENDING)])
            self.db.reports.create_index([("uploaded_at", DESCENDING)])
            self.db.reports.create_index([("filename", ASCENDING)])
            print("  📇 Reports indexes created")
            
            # Diagnosis history indexes
            self.db.diagnosis_history.create_index([("doc_id", ASCENDING)])
            self.db.diagnosis_history.create_index([("requester", ASCENDING)])
            self.db.diagnosis_history.create_index([("timestamp", DESCENDING)])
            self.db.diagnosis_history.create_index([("requester", ASCENDING), ("timestamp", DESCENDING)])
            print("  📇 Diagnosis history indexes created")
            
            print("✅ All indexes created successfully!")
            
        except Exception as e:
            print(f"❌ Index creation failed: {e}")
            raise
    
    def validate_schema(self):
        """Validate database schema"""
        print("🔍 Validating database schema...")
        
        try:
            required_collections = ["users", "reports", "diagnosis_history"]
            existing_collections = self.db.list_collection_names()
            
            missing_collections = [col for col in required_collections if col not in existing_collections]
            
            if missing_collections:
                print(f"❌ Missing collections: {missing_collections}")
                return False
            
            # Validate indexes
            for collection_name in required_collections:
                collection = self.db[collection_name]
                indexes = list(collection.list_indexes())
                print(f"  📇 {collection_name}: {len(indexes)} indexes")
            
            print("✅ Schema validation passed!")
            return True
            
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def seed_sample_data(self):
        """Seed database with sample data"""
        print("🌱 Seeding database with sample data...")
        
        try:
            # Sample users
            sample_users = [
                {
                    "username": "admin",
                    "password": self.hash_password("admin123"),
                    "role": "admin"
                },
                {
                    "username": "doctor1",
                    "password": self.hash_password("doctor123"),
                    "role": "doctor"
                },
                {
                    "username": "patient1",
                    "password": self.hash_password("patient123"),
                    "role": "patient"
                }
            ]
            
            # Insert users if they don't exist
            for user in sample_users:
                if not self.db.users.find_one({"username": user["username"]}):
                    self.db.users.insert_one(user)
                    print(f"  👤 Created user: {user['username']} ({user['role']})")
                else:
                    print(f"  👤 User already exists: {user['username']}")
            
            # Sample report metadata
            current_time = time.time()
            sample_reports = [
                {
                    "doc_id": "report_001",
                    "filename": "sample_blood_test.pdf",
                    "uploader": "doctor1",
                    "uploaded_at": current_time,
                    "num_chunks": 5
                },
                {
                    "doc_id": "report_002", 
                    "filename": "sample_xray_report.pdf",
                    "uploader": "doctor1",
                    "uploaded_at": current_time - 3600,
                    "num_chunks": 3
                }
            ]
            
            # Insert reports if they don't exist
            for report in sample_reports:
                if not self.db.reports.find_one({"doc_id": report["doc_id"]}):
                    self.db.reports.insert_one(report)
                    print(f"  📄 Created report: {report['filename']}")
                else:
                    print(f"  📄 Report already exists: {report['filename']}")
            
            # Sample diagnosis history
            sample_diagnoses = [
                {
                    "doc_id": "report_001",
                    "requester": "patient1",
                    "question": "What do my blood test results indicate?",
                    "answer": "Your blood test results show normal levels for most parameters.",
                    "sources": ["Blood Test Report - Page 1", "Reference Values - Page 2"],
                    "timestamp": current_time
                }
            ]
            
            # Insert diagnoses if they don't exist
            for diagnosis in sample_diagnoses:
                if not self.db.diagnosis_history.find_one({
                    "doc_id": diagnosis["doc_id"],
                    "requester": diagnosis["requester"],
                    "timestamp": diagnosis["timestamp"]
                }):
                    self.db.diagnosis_history.insert_one(diagnosis)
                    print(f"  🩺 Created diagnosis record for: {diagnosis['requester']}")
                else:
                    print(f"  🩺 Diagnosis record already exists")
            
            # Record migration
            self.record_migration("seed_data", "completed", "Sample data seeded")
            
            print("✅ Sample data seeding completed!")
            return True
            
        except Exception as e:
            print(f"❌ Sample data seeding failed: {e}")
            self.record_migration("seed_data", "failed", str(e))
            return False
    
    def run_migrations(self):
        """Run all pending migrations"""
        print("🔄 Running migrations...")
        
        try:
            # Check if database is initialized
            collections = self.db.list_collection_names()
            if not collections or "users" not in collections:
                print("📋 Database not initialized, running initialization...")
                if not self.init_database():
                    return False
            
            # Validate schema
            if not self.validate_schema():
                return False
            
            # Record migration
            self.record_migration("run_migrations", "completed", "All migrations completed")
            
            print("✅ All migrations completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            self.record_migration("run_migrations", "failed", str(e))
            return False
    
    def rollback_migration(self):
        """Rollback last migration (WARNING: This will drop collections)"""
        print("⚠️  ROLLBACK: This will drop all collections and data!")
        
        confirm = input("Are you sure you want to proceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("🚫 Rollback cancelled")
            return False
        
        try:
            # Drop all collections except migrations
            collections_to_drop = ["users", "reports", "diagnosis_history"]
            
            for collection_name in collections_to_drop:
                if collection_name in self.db.list_collection_names():
                    self.db.drop_collection(collection_name)
                    print(f"🗑️  Dropped collection: {collection_name}")
            
            # Record rollback
            self.record_migration("rollback", "completed", "Database rolled back")
            
            print("✅ Rollback completed!")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            self.record_migration("rollback", "failed", str(e))
            return False
    
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{self.db_name}_{timestamp}.json"
        
        print(f"💾 Creating backup: {backup_path}")
        
        try:
            backup_data = {}
            
            # Backup each collection
            for collection_name in ["users", "reports", "diagnosis_history", "migrations"]:
                if collection_name in self.db.list_collection_names():
                    collection_data = list(self.db[collection_name].find())
                    # Convert ObjectId to string for JSON serialization
                    for doc in collection_data:
                        if '_id' in doc:
                            doc['_id'] = str(doc['_id'])
                        if 'timestamp' in doc and hasattr(doc['timestamp'], 'isoformat'):
                            doc['timestamp'] = doc['timestamp'].isoformat()
                    
                    backup_data[collection_name] = collection_data
                    print(f"  💾 Backed up {collection_name}: {len(collection_data)} documents")
            
            # Write backup to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"✅ Backup created successfully: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="MongoDB Migration Script for Medical Diagnosis System")
    parser.add_argument("--action", 
                       choices=["init", "migrate", "rollback", "status", "seed", "backup"],
                       required=True,
                       help="Migration action to perform")
    parser.add_argument("--backup-path", 
                       help="Path for backup file (used with backup action)")
    
    args = parser.parse_args()
    
    # Initialize migration manager
    manager = MigrationManager()
    
    # Connect to database
    if not manager.connect():
        sys.exit(1)
    
    try:
        # Execute requested action
        success = False
        
        if args.action == "init":
            success = manager.init_database()
        elif args.action == "migrate":
            success = manager.run_migrations()
        elif args.action == "rollback":
            success = manager.rollback_migration()
        elif args.action == "status":
            manager.get_migration_status()
            success = True
        elif args.action == "seed":
            success = manager.seed_sample_data()
        elif args.action == "backup":
            success = manager.backup_database(args.backup_path)
        
        if success:
            print("\n🎉 Operation completed successfully!")
        else:
            print("\n💥 Operation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🚫 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    finally:
        manager.disconnect()

if __name__ == "__main__":
    main()