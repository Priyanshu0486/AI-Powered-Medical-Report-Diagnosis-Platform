# 🌩️ Cloudinary Integration Guide - Medical Report Diagnosis

## 📋 Overview

This guide shows you how to integrate Cloudinary cloud storage into your Medical Report Diagnosis application for secure, scalable document uploads.

## 🌟 Benefits of Using Cloudinary

- ✅ **Cloud Storage**: No local disk space limitations
- ✅ **Global CDN**: Fast file access worldwide  
- ✅ **Security**: Signed URLs for secure file access
- ✅ **Scalability**: Handle millions of files
- ✅ **Auto-optimization**: Automatic file compression
- ✅ **Free Tier**: 25GB storage + 25GB bandwidth/month
- ✅ **Easy Integration**: Simple API and SDK

## 🚀 Setup Steps

### Step 1: Create Cloudinary Account

1. **Sign up** at [cloudinary.com](https://cloudinary.com)
2. **Verify your email** and log in
3. **Go to Dashboard** to get your credentials

### Step 2: Get Your Credentials

From your Cloudinary Dashboard, copy:
- **Cloud Name**: `your-cloud-name`
- **API Key**: `123456789012345`  
- **API Secret**: `your-api-secret-here`

### Step 3: Configure Environment Variables

Add to your `.env` file:
```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-api-secret-here
```

### Step 4: Install Dependencies

The Cloudinary package is already added to `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 5: Update Your Main Server

Replace the import in `server/main.py`:
```python
# OLD
from .reports.route import router as report_router

# NEW - Use Cloudinary-enhanced route
from .reports.route_cloudinary import router as report_router
```

## 📂 File Structure

New files added for Cloudinary support:
```
server/reports/
├── cloudinary_service.py      # Cloudinary integration service
├── vectorstore_cloudinary.py  # Enhanced vectorstore with cloud support
└── route_cloudinary.py        # Enhanced API routes
```

## 🔧 How It Works

### Upload Process
1. **User uploads file** via Streamlit
2. **File sent to FastAPI** backend
3. **Auto-detection**: Cloudinary vs Local storage
4. **Cloudinary upload** with metadata
5. **Document processing** for AI embeddings
6. **Vector storage** in Pinecone
7. **Metadata storage** in MongoDB

### Storage Options
| Storage Type | When Used | Benefits |
|-------------|-----------|----------|
| **Cloudinary** | When credentials configured | Cloud storage, CDN, security |
| **Local** | Fallback or development | Simple, no external dependencies |

## 🛠️ API Endpoints

### New Enhanced Endpoints
- `POST /reports/upload` - Upload with auto-detection
- `GET /reports/list` - List user reports with signed URLs
- `GET /reports/download/{doc_id}` - Generate secure download URLs
- `DELETE /reports/delete/{doc_id}` - Delete reports and files
- `GET /reports/storage-status` - Check storage configuration

### Example Usage

#### Upload with Cloudinary
```python
# Auto-detects Cloudinary if configured
response = requests.post(
    f"{API_URL}/reports/upload",
    files=[('files', open('report.pdf', 'rb'))],
    auth=auth
)
```

#### Force Storage Type
```python
# Force Cloudinary
response = requests.post(
    f"{API_URL}/reports/upload?use_cloudinary=true",
    files=[('files', open('report.pdf', 'rb'))],
    auth=auth
)

# Force Local
response = requests.post(
    f"{API_URL}/reports/upload?use_cloudinary=false", 
    files=[('files', open('report.pdf', 'rb'))],
    auth=auth
)
```

## 🔒 Security Features

### Signed URLs
- **Temporary access**: URLs expire after 1 hour
- **User-specific**: Only file owner can access
- **Secure**: Cannot be guessed or shared

### Access Control
- **Authentication required**: Must be logged in
- **User isolation**: Users can only access their own files
- **Role-based**: Only patients can upload

## 📊 Monitoring

### Storage Status Check
```bash
curl http://localhost:8000/reports/storage-status
```

Response:
```json
{
  "cloudinary": {
    "configured": true,
    "cloud_name": "your-cloud-name"
  },
  "local_storage": {
    "available": true,
    "upload_dir": "./uploaded_reports"
  },
  "default_storage": "cloudinary"
}
```

## 🧪 Testing

### Test Cloudinary Integration
```python
# Test upload
files = [('files', open('sample_report.pdf', 'rb'))]
response = requests.post(
    'http://localhost:8000/reports/upload',
    files=files,
    auth=HTTPBasicAuth('patient_user', 'password')
)

print(response.json())
# Output: {
#   "message": "Reports uploaded and indexed successfully",
#   "doc_id": "uuid-here", 
#   "storage_type": "cloudinary",
#   "files_processed": 1,
#   "filenames": ["sample_report.pdf"]
# }
```

### Test File Listing
```python
response = requests.get(
    'http://localhost:8000/reports/list',
    auth=HTTPBasicAuth('patient_user', 'password')
)

print(response.json())
```

## 📈 Deployment Considerations

### Production Settings
- **Environment**: Set `ENVIRONMENT=production`
- **Secure URLs**: Always use HTTPS in production
- **API Limits**: Monitor Cloudinary usage
- **Backup**: Consider multi-cloud strategy

### Cloudinary Limits (Free Tier)
- **Storage**: 25GB
- **Bandwidth**: 25GB/month
- **Transformations**: 25,000/month
- **Requests**: 1M/month

### Scaling
- **Paid Plans**: Available for higher usage
- **Enterprise**: Custom solutions available
- **CDN**: Global edge locations

## 🚀 Deployment Commands

### Update Existing Installation
```bash
# Pull latest changes
git pull

# Install new dependencies  
pip install -r requirements.txt

# Add Cloudinary environment variables
# (Update your .env file)

# Restart application
python server/main.py
```

### Docker Deployment
Add to your `docker-compose.yml`:
```yaml
environment:
  - CLOUDINARY_CLOUD_NAME=${CLOUDINARY_CLOUD_NAME}
  - CLOUDINARY_API_KEY=${CLOUDINARY_API_KEY}  
  - CLOUDINARY_API_SECRET=${CLOUDINARY_API_SECRET}
```

## 🆘 Troubleshooting

### Common Issues

#### 1. "Cloudinary not configured" Error
**Solution**: Check environment variables
```bash
echo $CLOUDINARY_CLOUD_NAME
echo $CLOUDINARY_API_KEY
echo $CLOUDINARY_API_SECRET
```

#### 2. Upload Fails
**Causes**: 
- Invalid credentials
- File size too large (10MB limit)
- Unsupported file type

**Solution**: 
- Verify credentials in Cloudinary dashboard
- Check file size and type

#### 3. Download URLs Not Working
**Cause**: Signed URLs expired
**Solution**: Generate new URLs (valid for 1 hour)

### Debug Mode
Enable debug logging:
```bash
# In your .env file
DEBUG=true
```

## 📚 Resources

- **Cloudinary Docs**: https://cloudinary.com/documentation
- **Python SDK**: https://cloudinary.com/documentation/python_integration
- **API Reference**: https://cloudinary.com/documentation/image_upload_api_reference
- **Community**: https://community.cloudinary.com

## ✅ Migration from Local Storage

Your existing local files will continue to work. New uploads will automatically use Cloudinary if configured. To migrate existing files:

1. **Backup existing files**
2. **Re-upload through the application** (they'll go to Cloudinary)
3. **Update database records** (optional - for consistency)

The system supports both storage types simultaneously for smooth migration.