#!/usr/bin/env python3
"""
MongoDB Schema Seeding Script for Medical Report Diagnosis System

This script creates MongoDB collections with JSON Schema validation rules,
ensuring data integrity and consistency across the database.

Usage:
    python seed_schemas.py --action create      # Create schemas with validation
    python seed_schemas.py --action update      # Update existing schemas
    python seed_schemas.py --action validate    # Validate existing schemas
    python seed_schemas.py --action drop        # Drop schema validations
"""

import argparse
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class SchemaSeeder:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "rbac-diagnosis")
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.mongo_uri)
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
    
    def get_users_schema(self):
        """Define JSON schema for users collection"""
        return {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "password", "role"],
                "properties": {
                    "username": {
                        "bsonType": "string",
                        "description": "Username must be a string and is required",
                        "minLength": 3,
                        "maxLength": 50
                    },
                    "password": {
                        "bsonType": "string",
                        "description": "Password hash must be a string and is required",
                        "minLength": 6
                    },
                    "role": {
                        "enum": ["admin", "doctor", "patient"],
                        "description": "Role must be one of: admin, doctor, patient"
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                        "description": "Email must be a valid email format"
                    },
                    "full_name": {
                        "bsonType": "string",
                        "description": "Full name of the user"
                    },
                    "created_at": {
                        "bsonType": ["date", "double"],
                        "description": "Timestamp when user was created"
                    },
                    "last_login": {
                        "bsonType": ["date", "double"],
                        "description": "Timestamp of last login"
                    },
                    "is_active": {
                        "bsonType": "bool",
                        "description": "Whether the user account is active"
                    }
                }
            }
        }
    
    def get_reports_schema(self):
        """Define JSON schema for reports collection"""
        return {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["doc_id", "filename", "uploader", "uploaded_at"],
                "properties": {
                    "doc_id": {
                        "bsonType": "string",
                        "description": "Unique document identifier, required",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "filename": {
                        "bsonType": "string",
                        "description": "Original filename of the report, required",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "uploader": {
                        "bsonType": "string",
                        "description": "Username of the person who uploaded the report, required",
                        "minLength": 1
                    },
                    "uploaded_at": {
                        "bsonType": ["double", "date"],
                        "description": "Timestamp when report was uploaded, required"
                    },
                    "num_chunks": {
                        "bsonType": "int",
                        "minimum": 0,
                        "description": "Number of chunks the document is split into"
                    },
                    "file_size": {
                        "bsonType": ["int", "long"],
                        "minimum": 0,
                        "description": "Size of the file in bytes"
                    },
                    "file_type": {
                        "bsonType": "string",
                        "description": "MIME type of the file"
                    },
                    "status": {
                        "enum": ["uploaded", "processing", "processed", "failed"],
                        "description": "Processing status of the report"
                    },
                    "metadata": {
                        "bsonType": "object",
                        "description": "Additional metadata about the report",
                        "properties": {
                            "patient_name": {"bsonType": "string"},
                            "report_date": {"bsonType": ["date", "string"]},
                            "report_type": {"bsonType": "string"},
                            "doctor_name": {"bsonType": "string"}
                        }
                    },
                    "tags": {
                        "bsonType": "array",
                        "description": "Tags for categorizing reports",
                        "items": {
                            "bsonType": "string"
                        }
                    }
                }
            }
        }
    
    def get_diagnosis_history_schema(self):
        """Define JSON schema for diagnosis_history collection"""
        return {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["doc_id", "requester", "question", "answer", "timestamp"],
                "properties": {
                    "doc_id": {
                        "bsonType": "string",
                        "description": "Document ID being diagnosed, required",
                        "minLength": 1
                    },
                    "requester": {
                        "bsonType": "string",
                        "description": "Username of person requesting diagnosis, required",
                        "minLength": 1
                    },
                    "question": {
                        "bsonType": "string",
                        "description": "Question asked about the report, required",
                        "minLength": 1,
                        "maxLength": 2000
                    },
                    "answer": {
                        "bsonType": "string",
                        "description": "Diagnosis answer provided, required",
                        "minLength": 1
                    },
                    "sources": {
                        "bsonType": "array",
                        "description": "Source references used for diagnosis",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "timestamp": {
                        "bsonType": ["double", "date"],
                        "description": "Timestamp of diagnosis request, required"
                    },
                    "confidence_score": {
                        "bsonType": "double",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence score of the diagnosis"
                    },
                    "model_version": {
                        "bsonType": "string",
                        "description": "Version of the AI model used"
                    },
                    "processing_time": {
                        "bsonType": "double",
                        "minimum": 0,
                        "description": "Time taken to process in seconds"
                    },
                    "feedback": {
                        "bsonType": "object",
                        "description": "User feedback on the diagnosis",
                        "properties": {
                            "rating": {
                                "bsonType": "int",
                                "minimum": 1,
                                "maximum": 5
                            },
                            "comment": {"bsonType": "string"},
                            "feedback_date": {"bsonType": ["date", "double"]}
                        }
                    }
                }
            }
        }
    
    def get_migrations_schema(self):
        """Define JSON schema for migrations collection"""
        return {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "status", "timestamp"],
                "properties": {
                    "name": {
                        "bsonType": "string",
                        "description": "Migration name, required"
                    },
                    "status": {
                        "enum": ["completed", "failed", "pending"],
                        "description": "Migration status"
                    },
                    "timestamp": {
                        "bsonType": ["date", "double"],
                        "description": "When migration was executed, required"
                    },
                    "description": {
                        "bsonType": "string",
                        "description": "Description of the migration"
                    },
                    "version": {
                        "bsonType": "string",
                        "description": "Migration version number"
                    },
                    "rollback_info": {
                        "bsonType": "object",
                        "description": "Information needed for rollback"
                    }
                }
            }
        }
    
    def create_collection_with_schema(self, collection_name: str, schema: dict):
        """Create collection with schema validation"""
        try:
            # Check if collection exists
            if collection_name in self.db.list_collection_names():
                print(f"📋 Collection '{collection_name}' already exists")
                return False
            
            # Create collection with validation
            self.db.create_collection(
                collection_name,
                validator=schema,
                validationLevel="strict",
                validationAction="error"
            )
            print(f"✅ Created collection '{collection_name}' with schema validation")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create collection '{collection_name}': {e}")
            return False
    
    def update_collection_schema(self, collection_name: str, schema: dict):
        """Update existing collection schema validation"""
        try:
            # Update validation rules
            self.db.command({
                "collMod": collection_name,
                "validator": schema,
                "validationLevel": "strict",
                "validationAction": "error"
            })
            print(f"✅ Updated schema validation for '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update schema for '{collection_name}': {e}")
            return False
    
    def drop_collection_validation(self, collection_name: str):
        """Remove schema validation from collection"""
        try:
            self.db.command({
                "collMod": collection_name,
                "validator": {},
                "validationLevel": "off"
            })
            print(f"✅ Removed schema validation from '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove validation from '{collection_name}': {e}")
            return False
    
    def validate_existing_schemas(self):
        """Validate existing collection schemas"""
        print("🔍 Validating existing schemas...")
        
        collections = {
            "users": self.get_users_schema(),
            "reports": self.get_reports_schema(),
            "diagnosis_history": self.get_diagnosis_history_schema(),
            "migrations": self.get_migrations_schema()
        }
        
        existing_collections = self.db.list_collection_names()
        
        for collection_name, schema in collections.items():
            if collection_name in existing_collections:
                try:
                    # Get collection info
                    collection_info = self.db.command("listCollections", filter={"name": collection_name})
                    
                    if collection_info["cursor"]["firstBatch"]:
                        coll_data = collection_info["cursor"]["firstBatch"][0]
                        if "options" in coll_data and "validator" in coll_data["options"]:
                            print(f"✅ '{collection_name}' has schema validation")
                        else:
                            print(f"⚠️  '{collection_name}' exists but has no schema validation")
                    
                except Exception as e:
                    print(f"❌ Error validating '{collection_name}': {e}")
            else:
                print(f"⚠️  Collection '{collection_name}' does not exist")
        
        return True
    
    def create_all_schemas(self):
        """Create all collection schemas"""
        print("🚀 Creating all collection schemas...")
        
        schemas = {
            "users": self.get_users_schema(),
            "reports": self.get_reports_schema(),
            "diagnosis_history": self.get_diagnosis_history_schema(),
            "migrations": self.get_migrations_schema()
        }
        
        success_count = 0
        for collection_name, schema in schemas.items():
            if self.create_collection_with_schema(collection_name, schema):
                success_count += 1
        
        print(f"\n📊 Created {success_count}/{len(schemas)} schemas successfully")
        return success_count == len(schemas)
    
    def update_all_schemas(self):
        """Update all existing collection schemas"""
        print("🔄 Updating all collection schemas...")
        
        schemas = {
            "users": self.get_users_schema(),
            "reports": self.get_reports_schema(),
            "diagnosis_history": self.get_diagnosis_history_schema(),
            "migrations": self.get_migrations_schema()
        }
        
        success_count = 0
        existing_collections = self.db.list_collection_names()
        
        for collection_name, schema in schemas.items():
            if collection_name in existing_collections:
                if self.update_collection_schema(collection_name, schema):
                    success_count += 1
            else:
                print(f"⚠️  Collection '{collection_name}' does not exist, creating it...")
                if self.create_collection_with_schema(collection_name, schema):
                    success_count += 1
        
        print(f"\n📊 Updated {success_count}/{len(schemas)} schemas successfully")
        return success_count == len(schemas)
    
    def drop_all_validations(self):
        """Drop all schema validations"""
        print("⚠️  Dropping all schema validations...")
        
        confirm = input("Are you sure you want to drop all schema validations? (yes/no): ")
        if confirm.lower() != 'yes':
            print("🚫 Operation cancelled")
            return False
        
        collections = ["users", "reports", "diagnosis_history", "migrations"]
        existing_collections = self.db.list_collection_names()
        
        success_count = 0
        for collection_name in collections:
            if collection_name in existing_collections:
                if self.drop_collection_validation(collection_name):
                    success_count += 1
        
        print(f"\n📊 Dropped validation from {success_count} collections")
        return True
    
    def print_schema_info(self):
        """Print information about defined schemas"""
        print("\n📋 Defined Schema Structures:")
        print("=" * 60)
        
        schemas = {
            "users": "User accounts with roles (admin, doctor, patient)",
            "reports": "Medical reports uploaded by users",
            "diagnosis_history": "History of diagnosis queries and responses",
            "migrations": "Migration tracking and versioning"
        }
        
        for collection, description in schemas.items():
            print(f"\n📁 {collection.upper()}")
            print(f"   {description}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="MongoDB Schema Seeding Script for Medical Diagnosis System"
    )
    parser.add_argument(
        "--action",
        choices=["create", "update", "validate", "drop", "info"],
        required=True,
        help="Schema action to perform"
    )
    
    args = parser.parse_args()
    
    # Initialize schema seeder
    seeder = SchemaSeeder()
    
    # Handle info action without connection
    if args.action == "info":
        seeder.print_schema_info()
        return
    
    # Connect to database
    if not seeder.connect():
        sys.exit(1)
    
    try:
        success = False
        
        if args.action == "create":
            success = seeder.create_all_schemas()
        elif args.action == "update":
            success = seeder.update_all_schemas()
        elif args.action == "validate":
            success = seeder.validate_existing_schemas()
        elif args.action == "drop":
            success = seeder.drop_all_validations()
        
        if success:
            print("\n🎉 Schema operation completed successfully!")
        else:
            print("\n⚠️  Schema operation completed with warnings")
            
    except KeyboardInterrupt:
        print("\n🚫 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    finally:
        seeder.disconnect()


if __name__ == "__main__":
    main()
