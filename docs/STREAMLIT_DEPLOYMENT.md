# 🚀 Streamlit Deployment Guide - Medical Report Diagnosis

## 📋 Overview

This guide covers multiple deployment options for your Medical Report Diagnosis application on Streamlit platforms.

## 🌟 Deployment Options

### Option 1: Streamlit Community Cloud (FREE) ⭐ Recommended
### Option 2: Streamlit for Teams (PAID)
### Option 3: Self-Hosted Streamlit

---

## 🎯 Option 1: Streamlit Community Cloud (FREE)

### Prerequisites
- GitHub repository (public)
- GitHub account
- Streamlit Community Cloud account

### Step 1: Prepare Your Repository

1. **Create a separate repository for the Streamlit app** (recommended approach):
   ```bash
   # Create new repo structure
   mkdir medical-diagnosis-streamlit
   cd medical-diagnosis-streamlit
   
   # Copy necessary files
   cp -r ../Medical-Diagnosis/client/* .
   cp ../Medical-Diagnosis/requirements.txt .
   ```

2. **Or use the existing repository** (simpler approach)

### Step 2: Repository Structure for Streamlit Cloud

Your repository should look like this:
```
medical-diagnosis-streamlit/
├── app.py                 # Main Streamlit app (renamed from client/app.py)
├── requirements.txt       # Dependencies
├── .streamlit/           # Streamlit configuration
│   ├── config.toml       # App configuration
│   └── secrets.toml      # Environment variables (DO NOT COMMIT)
├── README.md             # Project description
└── pages/                # Additional pages (optional)
    └── admin.py          # Admin dashboard
```

### Step 3: Configuration Files

#### Create `.streamlit/config.toml`:
```toml
[global]
# Development settings
developmentMode = false
showWarningOnDirectExecution = false

[server]
# Server settings
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200
maxMessageSize = 200

[browser]
# Browser settings
serverAddress = "0.0.0.0"
gatherUsageStats = false
serverPort = 8501

[theme]
# App theme
primaryColor = "#1f77b4"
backgroundColor = "#ffffff" 
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
# Client settings
showErrorDetails = false
toolbarMode = "viewer"
```

#### Create `.streamlit/secrets.toml` (Local development only - DO NOT COMMIT):
```toml
# API Configuration
API_URL = "https://your-backend-api.herokuapp.com"  # Your deployed backend
MONGODB_URL = "mongodb+srv://username:password@cluster.mongodb.net/"
DATABASE_NAME = "medical_diagnosis"

# Pinecone Configuration
PINECONE_API_KEY = "your_pinecone_api_key"
PINECONE_INDEX_NAME = "medical-reports"

# Optional
HUGGINGFACE_API_TOKEN = "your_hf_token"
```

### Step 4: Update app.py for Streamlit Cloud

Create the main `app.py` file:
```python
import streamlit as st
import requests
import json
from requests.auth import HTTPBasicAuth
import datetime
import os

# Streamlit Cloud configuration
st.set_page_config(
    page_title="🏥 Medical Report Diagnosis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/medical-diagnosis',
        'Report a bug': 'https://github.com/your-username/medical-diagnosis/issues',
        'About': "# Medical Report Diagnosis System\nAI-powered medical report analysis and diagnosis assistance."
    }
)

# Configuration - Use Streamlit secrets in production
if "API_URL" in st.secrets:
    API_URL = st.secrets["API_URL"]
else:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

# Add error handling for API connection
def check_api_connection():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Main app logic
def main():
    # Check API connection
    if not check_api_connection():
        st.error(f"⚠️ Cannot connect to backend API at {API_URL}")
        st.info("Please ensure the backend server is running or contact support.")
        st.stop()
    
    # Your existing app logic here...
    st.title("🏥 Medical Report Diagnosis")
    st.success(f"✅ Connected to backend API: {API_URL}")
    
    # Add your existing Streamlit app code here

if __name__ == "__main__":
    main()
```

### Step 5: Deploy to Streamlit Community Cloud

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Streamlit deployment"
   git branch -M main
   git remote add origin https://github.com/your-username/medical-diagnosis-streamlit.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `app.py`
   - Click "Deploy!"

3. **Configure Secrets** (after deployment):
   - Go to your app dashboard
   - Click "Settings" → "Secrets"
   - Add your environment variables:
   ```toml
   API_URL = "https://your-backend-api-url.com"
   MONGODB_URL = "mongodb+srv://username:password@cluster.mongodb.net/"
   # Add other secrets as needed
   ```

---

## 🏢 Option 2: Streamlit for Teams (PAID)

For enterprise deployment with more features:

### Features:
- Private repositories
- Custom domains
- SSO integration
- Advanced security
- Priority support

### Setup:
1. Subscribe to Streamlit for Teams
2. Follow similar setup as Community Cloud
3. Access advanced features through dashboard

---

## 🖥️ Option 3: Self-Hosted Streamlit

Deploy on your own infrastructure:

### Using Docker:
```dockerfile
# Dockerfile.streamlit
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Using Docker Compose:
```yaml
# docker-compose.streamlit.yml
version: '3.8'

services:
  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./uploaded_reports:/app/uploaded_reports
    restart: unless-stopped

  backend:
    # Your existing backend configuration
    ports:
      - "8000:8000"
```

---

## 🔄 Backend Deployment Options

Since Streamlit needs a backend API, here are deployment options:

### Option A: Heroku (Simple)
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn server.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-medical-api
git subtree push --prefix=server heroku main
```

### Option B: Railway (Modern)
```yaml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn server.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "always"
```

### Option C: Render (Free tier available)
```yaml
# render.yaml
services:
  - type: web
    name: medical-diagnosis-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn server.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: "/health"
```

---

## 📋 Complete Deployment Checklist

### Pre-Deployment
- [ ] Backend API deployed and accessible
- [ ] MongoDB Atlas configured
- [ ] Pinecone index created
- [ ] Environment variables secured
- [ ] Repository structure organized

### Streamlit Specific
- [ ] `app.py` configured for production
- [ ] `requirements.txt` updated
- [ ] `.streamlit/config.toml` created
- [ ] Secrets configured (not committed)
- [ ] Error handling implemented
- [ ] Health checks added

### Post-Deployment
- [ ] App loads without errors
- [ ] API connection working
- [ ] File uploads functional
- [ ] Database operations working
- [ ] All features tested

---

## 🛠️ Troubleshooting

### Common Issues:

**1. API Connection Errors**
```python
# Add retry logic
import time

def api_request_with_retry(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            return response
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise
```

**2. File Upload Issues**
```python
# Handle large files
st.file_uploader(
    "Upload Medical Report",
    type=['pdf'],
    help="Maximum file size: 200MB"
)
```

**3. Secrets Not Loading**
```python
# Check if running on Streamlit Cloud
def get_config(key, default=None):
    if hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

API_URL = get_config("API_URL", "http://localhost:8000")
```

---

## 🎯 Production Optimization

### Performance:
```python
# Cache API calls
@st.cache_data(ttl=300)  # 5-minute cache
def fetch_user_reports(user_id):
    response = requests.get(f"{API_URL}/reports/{user_id}")
    return response.json()

# Cache expensive operations
@st.cache_resource
def load_model_info():
    # Load model information once
    pass
```

### Security:
```python
# Validate inputs
def sanitize_input(text):
    import re
    return re.sub(r'[<>"\']', '', text)

# Add rate limiting info
st.info("API calls are rate-limited. Please wait between requests.")
```

---

## 🔗 Useful Links

- [Streamlit Community Cloud](https://share.streamlit.io)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Deployment Best Practices](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

---

## 📞 Support

If you encounter issues:
1. Check Streamlit Community forums
2. Review deployment logs
3. Test backend API independently
4. Verify all environment variables
5. Contact Streamlit support for cloud issues

---

🎉 **Your Medical Report Diagnosis app is now ready for Streamlit deployment!**