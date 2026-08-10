# MongoDB Schema Seeding Guide

## Overview

This guide explains how to use the schema seeding script to create and manage MongoDB collection schemas with validation rules for the Medical Report Diagnosis System.

## What is Schema Seeding?

Schema seeding creates MongoDB collections with **JSON Schema validation** rules that:
- Enforce data types and formats
- Validate required fields
- Restrict allowed values (enums)
- Ensure data integrity across the application
- Prevent invalid data from being inserted

## Prerequisites

1. **MongoDB Server**: Running locally or accessible via URI
2. **Python 3.7+**: Installed and in PATH
3. **Dependencies**: Install via `pip install -r migration_requirements.txt`
4. **Environment Variables**: Configure in `.env`:
   ```env
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=rbac-diagnosis
   ```

## Quick Start

### Option 1: PowerShell Script (Recommended for Windows)
```powershell
.\scripts\seed_schemas.ps1
```

### Option 2: Batch Script
```batch
scripts\seed_schemas.bat
```

### Option 3: Direct Python Command
```bash
python scripts/seed_schemas.py --action create
```

## Available Actions

### 1. Create Schemas (`create`)
Creates new collections with schema validation rules.

**Usage:**
```bash
python scripts/seed_schemas.py --action create
```

**What it does:**
- Creates `users` collection with validation
- Creates `reports` collection with validation
- Creates `diagnosis_history` collection with validation
- Creates `migrations` collection with validation
- Skips if collections already exist

**When to use:**
- First-time database setup
- Creating new collections
- After database reset

---

### 2. Update Schemas (`update`)
Updates validation rules on existing collections or creates missing ones.

**Usage:**
```bash
python scripts/seed_schemas.py --action update
```

**What it does:**
- Updates existing collection validators
- Creates collections if they don't exist
- Applies new validation rules without data loss

**When to use:**
- After modifying schema definitions
- Adding new validation rules
- Updating field constraints

---

### 3. Validate Schemas (`validate`)
Checks if collections have schema validation enabled.

**Usage:**
```bash
python scripts/seed_schemas.py --action validate
```

**What it does:**
- Lists all collections
- Shows which have validation
- Reports missing validations

**When to use:**
- Verifying schema setup
- Troubleshooting validation issues
- Auditing database configuration

---

### 4. Drop Validations (`drop`)
Removes schema validation from collections (⚠️ requires confirmation).

**Usage:**
```bash
python scripts/seed_schemas.py --action drop
```

**What it does:**
- Removes all validation rules
- Keeps collections and data intact
- Requires user confirmation

**When to use:**
- Temporarily disabling validation
- Testing without constraints
- Before major data migrations

---

### 5. Show Schema Info (`info`)
Displays information about defined schemas (no DB connection needed).

**Usage:**
```bash
python scripts/seed_schemas.py --action info
```

**What it does:**
- Shows all schema structures
- Lists validation rules
- Displays field descriptions

**When to use:**
- Documentation reference
- Understanding schema structure
- Planning schema changes

---

## Schema Definitions

### 👤 Users Collection

**Required Fields:**
- `username` (string, 3-50 chars, unique)
- `password` (string, min 6 chars, hashed)
- `role` (enum: admin, doctor, patient)

**Optional Fields:**
- `email` (string, valid email format)
- `full_name` (string)
- `created_at` (date/timestamp)
- `last_login` (date/timestamp)
- `is_active` (boolean)

**Validation Rules:**
```json
{
  "username": {
    "minLength": 3,
    "maxLength": 50
  },
  "role": {
    "enum": ["admin", "doctor", "patient"]
  },
  "email": {
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  }
}
```

---

### 📄 Reports Collection

**Required Fields:**
- `doc_id` (string, 1-100 chars, unique)
- `filename` (string, 1-255 chars)
- `uploader` (string, username reference)
- `uploaded_at` (timestamp)

**Optional Fields:**
- `num_chunks` (int, ≥0)
- `file_size` (int/long, ≥0)
- `file_type` (string, MIME type)
- `status` (enum: uploaded, processing, processed, failed)
- `metadata` (object with patient info, report date, etc.)
- `tags` (array of strings)

**Validation Rules:**
```json
{
  "doc_id": {
    "minLength": 1,
    "maxLength": 100
  },
  "status": {
    "enum": ["uploaded", "processing", "processed", "failed"]
  },
  "num_chunks": {
    "minimum": 0
  }
}
```

---

### 🩺 Diagnosis History Collection

**Required Fields:**
- `doc_id` (string, references report)
- `requester` (string, username)
- `question` (string, 1-2000 chars)
- `answer` (string)
- `timestamp` (timestamp)

**Optional Fields:**
- `sources` (array of strings)
- `confidence_score` (double, 0.0-1.0)
- `model_version` (string)
- `processing_time` (double, ≥0)
- `feedback` (object with rating, comment, date)

**Validation Rules:**
```json
{
  "question": {
    "minLength": 1,
    "maxLength": 2000
  },
  "confidence_score": {
    "minimum": 0.0,
    "maximum": 1.0
  },
  "feedback.rating": {
    "minimum": 1,
    "maximum": 5
  }
}
```

---

### 📋 Migrations Collection

**Required Fields:**
- `name` (string)
- `status` (enum: completed, failed, pending)
- `timestamp` (date/timestamp)

**Optional Fields:**
- `description` (string)
- `version` (string)
- `rollback_info` (object)

---

## Validation Levels

The schemas are created with:
- **validationLevel**: `strict` - All inserts and updates must match schema
- **validationAction**: `error` - Invalid operations are rejected with error

## Common Workflows

### Initial Setup
```bash
# 1. Create schemas
python scripts/seed_schemas.py --action create

# 2. Verify creation
python scripts/seed_schemas.py --action validate

# 3. Run database initialization (creates indexes)
python scripts/migrate_db.py --action init

# 4. Seed sample data
python scripts/migrate_db.py --action seed
```

### Schema Updates
```bash
# 1. Backup database
python scripts/migrate_db.py --action backup

# 2. Update schemas in code (edit seed_schemas.py)

# 3. Apply updates
python scripts/seed_schemas.py --action update

# 4. Validate changes
python scripts/seed_schemas.py --action validate
```

### Troubleshooting Invalid Data
```bash
# 1. Drop validations temporarily
python scripts/seed_schemas.py --action drop

# 2. Fix data issues (manual or scripted)

# 3. Re-apply validations
python scripts/seed_schemas.py --action update
```

## Best Practices

1. **Always create schemas before data insertion** to enforce validation from the start
2. **Backup before schema updates** in production environments
3. **Test schema changes** in development first
4. **Document custom validation rules** when modifying schemas
5. **Use semantic versioning** for schema changes
6. **Monitor validation errors** in application logs

## Error Handling

### Common Errors

**Error: "Collection already exists"**
- Use `--action update` instead of `create`

**Error: "Document failed validation"**
- Check document against schema rules
- Use `--action info` to see requirements

**Error: "Connection refused"**
- Verify MongoDB is running
- Check `MONGO_URI` in `.env`

**Error: "Permission denied"**
- Ensure MongoDB user has write permissions
- Check authentication settings

## Integration with Application

The schemas work seamlessly with your existing code:

```python
# In server/config/db.py
from pymongo import MongoClient

# Collections automatically enforce validation
users_collection = db["users"]

# This will succeed
users_collection.insert_one({
    "username": "john_doe",
    "password": "hashed_password",
    "role": "patient"
})

# This will fail (invalid role)
users_collection.insert_one({
    "username": "jane_doe",
    "password": "hashed_password",
    "role": "invalid_role"  # ❌ Not in enum
})
```

## Monitoring and Maintenance

### Check Schema Status
```bash
python seed_schemas.py --action validate
```

### Update After Code Changes
```bash
python seed_schemas.py --action update
```

### Review Schema Definitions
```bash
python seed_schemas.py --action info
```

## Advanced Usage

### Modifying Schemas

Edit `seed_schemas.py` and modify the schema methods:

```python
def get_users_schema(self):
    return {
        "$jsonSchema": {
            "properties": {
                "new_field": {
                    "bsonType": "string",
                    "description": "New field description"
                }
            }
        }
    }
```

Then apply:
```bash
python seed_schemas.py --action update
```

### Custom Validation Rules

Add complex validation patterns:

```python
"email": {
    "bsonType": "string",
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
}
```

## Related Scripts

- `scripts/migrate_db.py` - Database initialization and migrations
- `MIGRATION_GUIDE.md` - Database migration documentation
- `scripts/seed_schemas.py` - This schema seeding script

## Support

For issues or questions:
1. Check MongoDB logs: `mongod.log`
2. Review application logs
3. Validate schema syntax: `python scripts/seed_schemas.py --action info`
4. Test connection: `python scripts/seed_schemas.py --action validate`

## Summary

The schema seeding script provides a robust way to enforce data integrity in your MongoDB database by:
- ✅ Creating collections with validation
- ✅ Enforcing data types and formats
- ✅ Preventing invalid data insertion
- ✅ Documenting schema structure
- ✅ Making schema updates manageable

Use it as part of your deployment pipeline for consistent database configuration across environments.
