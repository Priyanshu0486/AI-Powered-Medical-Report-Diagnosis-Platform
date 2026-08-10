# Database Migration Guide

This guide explains how to use the MongoDB migration script for the Medical Report Diagnosis System.

## Prerequisites

1. **MongoDB Server**: Ensure MongoDB is running locally or update the `MONGO_URI` in your `.env` file
2. **Python Dependencies**: Install required packages
   ```bash
   pip install -r migration_requirements.txt
   ```
3. **Environment Variables**: Ensure your `.env` file contains:
   ```
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=rbac-diagnosis
   ```

## Migration Commands

### 1. Initialize Database
Creates collections and indexes for the first time:
```bash
python scripts/migrate_db.py --action init
```

### 2. Run Migrations
Runs all pending migrations and validates schema:
```bash
python scripts/migrate_db.py --action migrate
```

### 3. Check Migration Status
View current migration status and history:
```bash
python scripts/migrate_db.py --action status
```

### 4. Seed Sample Data
Add sample users, reports, and diagnosis records for testing:
```bash
python scripts/migrate_db.py --action seed
```

### 5. Create Backup
Backup current database to JSON file:
```bash
python scripts/migrate_db.py --action backup
# Or specify custom backup path:
python scripts/migrate_db.py --action backup --backup-path ./backups/my_backup.json
```

### 6. Rollback Database (⚠️ DESTRUCTIVE)
**WARNING**: This will drop all collections and data!
```bash
python scripts/migrate_db.py --action rollback
```

## Database Schema

The migration script creates the following collections:

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string (unique)",
  "password": "string (hashed)",
  "role": "string (admin|doctor|patient)"
}
```

### Reports Collection  
```json
{
  "_id": "ObjectId",
  "doc_id": "string (unique)",
  "filename": "string",
  "uploader": "string",
  "uploaded_at": "float (timestamp)",
  "num_chunks": "number"
}
```

### Diagnosis History Collection
```json
{
  "_id": "ObjectId", 
  "doc_id": "string",
  "requester": "string",
  "question": "string",
  "answer": "string",
  "sources": ["array of strings"],
  "timestamp": "float"
}
```

### Migrations Collection (System)
```json
{
  "_id": "ObjectId",
  "name": "string",
  "status": "string (completed|failed)",
  "timestamp": "datetime",
  "description": "string"
}
```

## Indexes Created

### Users Collection
- `username` (unique)
- `role`

### Reports Collection
- `doc_id` (unique)
- `uploader`
- `uploaded_at` (descending)
- `filename`

### Diagnosis History Collection
- `doc_id`
- `requester`
- `timestamp` (descending)
- `requester + timestamp` (compound, descending)

## Sample Data

When using `--action seed`, the following sample data is created:

**Users:**
- `admin` / `admin123` (admin role)
- `doctor1` / `doctor123` (doctor role)  
- `patient1` / `patient123` (patient role)

**Reports:**
- Sample blood test report
- Sample X-ray report

**Diagnosis History:**
- Sample diagnosis record for patient1

## Troubleshooting

### Connection Issues
- Verify MongoDB is running: `mongosh` or check service status
- Check `MONGO_URI` in `.env` file
- Ensure network connectivity to MongoDB server

### Permission Issues
- Ensure user has read/write permissions to database
- Check MongoDB authentication if enabled

### Schema Validation Errors
- Run `python scripts/migrate_db.py --action status` to check current state
- Consider running `--action init` if collections are missing

### Backup/Restore
- Always create backups before major migrations
- Backup files are in JSON format and can be imported manually if needed

## Best Practices

1. **Always backup before migrations** in production
2. **Test migrations** in development environment first  
3. **Review migration status** after each operation
4. **Monitor database performance** after index creation
5. **Use semantic versioning** for migration tracking

## Migration Workflow

For a new deployment:
```bash
# 1. Initialize database
python scripts/migrate_db.py --action init

# 2. Seed with sample data (optional, for development)
python scripts/migrate_db.py --action seed

# 3. Check status
python scripts/migrate_db.py --action status
```

For existing database:
```bash
# 1. Create backup
python scripts/migrate_db.py --action backup

# 2. Run migrations  
python scripts/migrate_db.py --action migrate

# 3. Validate
python scripts/migrate_db.py --action status
```