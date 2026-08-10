# 🏥 Medical Report Diagnosis System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-brightgreen.svg)](https://www.mongodb.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

A comprehensive **AI-powered medical diagnosis platform** built with FastAPI that enables healthcare professionals to upload medical reports, extract insights using advanced AI, and generate accurate diagnoses through intelligent document analysis and retrieval-augmented generation (RAG).

---

## 🎯 Overview

An intelligent **AI-powered medical diagnosis platform** that leverages advanced machine learning and natural language processing to analyze medical reports and provide accurate diagnostic insights. Built with FastAPI backend, MongoDB database, and Streamlit frontend for seamless healthcare document analysis.

This comprehensive medical diagnosis system combines the power of artificial intelligence with modern web technologies to assist healthcare professionals in analyzing medical reports. The platform uses **Retrieval-Augmented Generation (RAG)** with **LLaMA 3** through Groq API to provide contextually accurate medical diagnoses based on uploaded PDF reports.

### Key Highlights
- 🤖 **AI-Powered Diagnosis** using state-of-the-art LLM technology
- 🔐 **Secure Role-Based Access** for doctors and patients
- 📄 **Advanced PDF Processing** with text extraction and chunking
- 🔍 **Vector Search** capabilities with Pinecone integration
- 📊 **Comprehensive Dashboard** for report management
- 🏥 **Healthcare-Focused** design and workflow

---

## 🚀 Core Features

✅ **Role-based Authentication** (Doctor / Patient)

✅ **PDF Report Upload** with secure file handling

✅ **Text Extraction & Chunking** from PDFs using advanced parsing

✅ **AI Diagnosis Generation** using **Groq LLaMA 3** integration

✅ **Vector Storage with Pinecone** for RAG retrieval and semantic search

✅ **MongoDB Integration** for user, report, and diagnosis records management

✅ **Role-based Access Control** for viewing and requesting diagnoses

✅ **Real-time Processing** with progress tracking and notifications

✅ **Medical History Management** for comprehensive patient care tracking

✅ **Secure File Storage** with organized directory structure and encryption

✅ **Cloudinary Integration** for cloud-based file storage and CDN delivery

---

## 🌩️ Cloudinary File Upload

### Overview
The system supports both **local storage** and **Cloudinary cloud storage** for medical report uploads. Cloudinary provides secure, scalable cloud storage with global CDN delivery and automatic file optimization.

### 🌟 Cloudinary Benefits
- ✅ **Cloud Storage**: No local disk space limitations
- ✅ **Global CDN**: Fast file access worldwide  
- ✅ **Security**: Signed URLs for secure file access
- ✅ **Scalability**: Handle millions of files
- ✅ **Auto-optimization**: Automatic file compression
- ✅ **Free Tier**: 25GB storage + 25GB bandwidth/month

### 🚀 Quick Setup

#### 1. Create Cloudinary Account
1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Get your credentials from the Dashboard:
   - **Cloud Name**: `your-cloud-name`
   - **API Key**: `123456789012345`  
   - **API Secret**: `your-api-secret-here`

#### 2. Configure Environment Variables
Add to your `.env` file:
```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-api-secret-here
```

#### 3. Enhanced API Endpoints
| Method | Endpoint | Description | Features |
|--------|----------|-------------|----------|
| POST | `/reports/upload` | Upload with auto-detection | Cloudinary/Local fallback |
| GET | `/reports/list` | List reports with signed URLs | Secure access links |
| GET | `/reports/download/{doc_id}` | Generate secure download URLs | Temporary access (1hr) |
| GET | `/reports/storage-status` | Check storage configuration | System status |

#### 4. Usage Examples
```python
# Auto-detects Cloudinary if configured
response = requests.post(
    f"{API_URL}/reports/upload",
    files=[('files', open('report.pdf', 'rb'))],
    auth=auth
)

# Force Cloudinary storage
response = requests.post(
    f"{API_URL}/reports/upload?use_cloudinary=true",
    files=[('files', open('report.pdf', 'rb'))],
    auth=auth
)
```

### 🔒 Security Features
- **Signed URLs**: Temporary access with 1-hour expiration
- **User-specific**: Only file owner can access
- **Authentication**: JWT token required for all operations
- **Role-based**: Patients can upload, doctors can view

### 📊 Storage Status Check
```bash
curl http://localhost:8000/reports/storage-status
```

**Response:**
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

> **Note**: The system automatically falls back to local storage if Cloudinary is not configured, ensuring seamless operation in all environments.

---

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** MongoDB (Document Storage)
- **Vector DB:** Pinecone (Semantic Search & RAG)
- **AI/LLM:** Groq API (LLaMA 3 Model)
- **Authentication:** JWT Token-based Security

### Frontend
- **Framework:** Streamlit
- **UI Components:** Custom healthcare-focused interface
- **File Upload:** Drag-and-drop PDF support

### Processing & AI
- **PDF Processing:** PyPDF2 (Text Extraction)
- **Text Processing:** Advanced chunking and preprocessing
- **Vector Embeddings:** Semantic text representation
- **RAG System:** Contextual information retrieval

### Infrastructure
- **Environment:** Python 3.10+
- **File Storage:** Secure local storage with UUID naming
- **Cloud Storage:** Cloudinary integration for scalable file management
- **API Documentation:** OpenAPI/Swagger integration

---

## 📂 Project Structure

```
Medical-Diagnosis/
├── 📁 assets/                          # Static assets and documentation
│   ├── 📋 ProjectReport.pdf            # Comprehensive project documentation
│   ├── 📄 report1.pdf                  # Sample medical report
│   ├── 📄 sample-report.pdf            # Demo medical document
│   └── 🖼️ Various UI screenshots       # Application interface previews
├── 📁 client/                          # Frontend Streamlit application
│   ├── 🐍 app.py                       # Main Streamlit application
│   └── 📋 requirements.txt             # Frontend dependencies
├── 📁 server/                          # FastAPI backend server
│   ├── 🐍 main.py                      # FastAPI application entry point
│   ├── 📁 auth/                        # Authentication & authorization
│   │   ├── 🐍 hash_utils.py            # Password hashing utilities
│   │   ├── 🐍 models.py                # Auth data models & schemas
│   │   └── 🐍 route.py                 # Authentication API endpoints
│   ├── 📁 config/                      # System configuration
│   │   └── 🐍 db.py                    # Database connection setup
│   ├── 📁 diagnosis/                   # AI diagnosis processing
│   │   ├── 🐍 query.py                 # LLM query processing logic
│   │   └── 🐍 route.py                 # Diagnosis API endpoints
│   ├── 📁 models/                      # Database models
│   │   └── 🐍 db_models.py             # MongoDB document schemas
│   └── 📁 reports/                     # Report management system
│       ├── 🐍 route.py                 # Report upload/management APIs
│       └── 🐍 vectorstore.py           # Pinecone vector operations
├── 📁 uploaded_dir/                    # Secure file storage
│   ├── 📄 UUID-named medical reports   # Uploaded documents (secured)
│   └── 📄 Various PDF files            # Sample and user reports
├── 🐍 main.py                          # Project main entry point
├── ⚙️ pyproject.toml                   # Project configuration & metadata
├── 📋 requirements.txt                 # Python dependencies
└── 📖 README.md                        # This documentation file
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10 or higher
- MongoDB instance (local or cloud)
- Pinecone account and API key
- Groq API key for LLaMA 3 access

### 1️⃣ Clone Repository

```bash
git clone <your-repository-url>
cd Medical-Diagnosis
```

### 2️⃣ Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
MONGO_URI=mongodb://localhost:27017/
DB_NAME=medical_diagnosis

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=medical-reports-index
PINECONE_ENV=your_pinecone_environment

# AI/LLM Services
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Cloudinary Configuration (Optional - for cloud storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-api-secret-here

# Application Settings
UPLOAD_DIR=./uploaded_dir
API_URL=http://localhost:8000

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Additional Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

### 5️⃣ Launch Application

#### Start Backend Server
```bash
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Client (New Terminal)
```bash
cd client
streamlit run app.py --server.port 8501
```

### 6️⃣ Access Application

- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend Interface:** [http://localhost:8501](http://localhost:8501)

---

## 📡 API Reference

### 🔐 Authentication Endpoints

| Method | Endpoint        | Description                | Request Body                    |
|--------|-----------------|----------------------------|---------------------------------|
| POST   | `/auth/signup`  | Register new user          | `{username, email, password, role}` |
| POST   | `/auth/login`   | User login & get token     | `{username, password}`          |
| GET    | `/auth/profile` | Get current user info      | *Requires JWT token*            |
| PUT    | `/auth/profile` | Update user profile        | `{email, full_name, ...}`       |

### 📄 Report Management

| Method | Endpoint                | Description                | Access Level    |
|--------|-------------------------|----------------------------|-----------------|
| POST   | `/reports/upload`       | Upload medical report PDF  | Patient/Doctor  |
| GET    | `/reports/`             | List user's reports        | Patient/Doctor  |
| GET    | `/reports/list`         | List reports with signed URLs | Patient/Doctor  |
| GET    | `/reports/{report_id}`  | Get specific report        | Owner/Doctor    |
| GET    | `/reports/download/{doc_id}` | Generate secure download URLs | Owner/Doctor |
| DELETE | `/reports/{report_id}`  | Delete report              | Owner only      |
| DELETE | `/reports/delete/{doc_id}` | Delete reports and files | Owner only      |
| GET    | `/reports/search`       | Search reports by criteria| Doctor only     |
| GET    | `/reports/storage-status` | Check storage configuration | Admin/Public |

### 🧠 AI Diagnosis

| Method | Endpoint                     | Description                    | Access Level |
|--------|------------------------------|--------------------------------|--------------|
| POST   | `/diagnosis/generate`        | Create AI diagnosis            | Doctor only  |
| GET    | `/diagnosis/patient/{id}`    | Get patient's diagnoses        | Doctor only  |
| GET    | `/diagnosis/my-diagnoses`    | Get own diagnoses              | Patient      |
| PUT    | `/diagnosis/{diagnosis_id}`  | Update diagnosis               | Doctor only  |
| GET    | `/diagnosis/export/{id}`     | Export diagnosis report        | Owner/Doctor |

### 🔧 System Endpoints

| Method | Endpoint     | Description              | Access Level |
|--------|--------------|--------------------------|--------------|
| GET    | `/health`    | System health check      | Public       |
| GET    | `/stats`     | Application statistics   | Admin        |
| GET    | `/docs`      | API documentation        | Public       |

---

## 🏗️ System Architecture

### RAG (Retrieval-Augmented Generation) Pipeline

The system implements a sophisticated RAG pipeline:

1. **Document Processing:** PDF upload and text extraction
2. **Text Chunking:** Intelligent document segmentation
3. **Vector Embedding:** Semantic text representation
4. **Vector Storage:** Pinecone database integration
5. **Context Retrieval:** Relevant information extraction
6. **AI Generation:** LLaMA 3 powered diagnosis generation

### Application Workflow

1. **User Authentication:** Secure login with JWT tokens
2. **Report Upload:** PDF processing and text extraction
3. **Vector Processing:** Text chunking and embedding generation
4. **Storage:** Documents stored in MongoDB, vectors in Pinecone
5. **Diagnosis Request:** Doctor initiates AI diagnosis
6. **RAG Processing:** Relevant context retrieval from vector store
7. **AI Generation:** LLaMA 3 generates diagnosis based on context
8. **Result Delivery:** Formatted diagnosis presented to user

---

## 🧪 Testing & Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=server tests/
```

### Development Mode
```bash
# Backend with auto-reload
uvicorn server.main:app --reload --log-level debug

# Frontend with auto-refresh
streamlit run client/app.py --server.runOnSave true
```

### Database Setup
```bash
# Start MongoDB (if using Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Initialize database (optional)
python scripts/init_db.py
```

---

## 🔧 Configuration Options

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MONGO_URI` | MongoDB connection string | ✅ | - |
| `DB_NAME` | Database name | ✅ | - |
| `PINECONE_API_KEY` | Pinecone API key | ✅ | - |
| `GROQ_API_KEY` | Groq API key for LLaMA 3 | ✅ | - |
| `SECRET_KEY` | JWT signing key | ✅ | - |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | ❌ | - |
| `CLOUDINARY_API_KEY` | Cloudinary API key | ❌ | - |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | ❌ | - |
| `UPLOAD_DIR` | File upload directory | ❌ | `./uploads` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | ❌ | `10MB` |
| `DEBUG` | Debug mode | ❌ | `False` |

---

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t medical-diagnosis .

# Run container
docker run -p 8000:8000 --env-file .env medical-diagnosis
```

### Production Considerations
- Use environment-specific `.env` files
- Configure reverse proxy (nginx/Apache)
- Set up SSL certificates
- Implement proper logging and monitoring
- Regular database backups
- Security headers and CORS configuration

---

## 🛡️ Security Features

- **JWT Authentication:** Secure token-based authentication
- **Role-Based Access:** Doctor/Patient permission levels
- **File Upload Security:** Type validation and size limits
- **Data Encryption:** Sensitive data encryption at rest
- **API Rate Limiting:** Prevent abuse and DoS attacks
- **Input Validation:** Comprehensive request validation
- **HIPAA Compliance Ready:** Healthcare data protection standards

---

## 📊 Performance & Monitoring

### Metrics Tracked
- API response times
- File upload/processing duration
- Database query performance
- AI model inference latency
- User activity and engagement

### Optimization Features
- Asynchronous processing for large files
- Database indexing for fast queries
- Vector search optimization
- Caching for frequently accessed data
- Connection pooling for database efficiency

---

## 🔮 Future Roadmap

### Short-term (Next Release)
- [ ] **Enhanced UI/UX** with modern design system
- [ ] **Batch Report Processing** for multiple file uploads
- [ ] **Export Functionality** (PDF, Word, Excel)
- [ ] **Email Notifications** for diagnosis completion
- [ ] **Advanced Search** with filters and sorting

### Medium-term (3-6 months)
- [ ] **Multiple AI Models** (GPT-4, Claude, Gemini)
- [ ] **Image Analysis** for X-rays and scans
- [ ] **Mobile Application** (React Native/Flutter)
- [ ] **Real-time Collaboration** for medical teams
- [ ] **Integration APIs** for hospital systems

### Long-term (6+ months)
- [ ] **Machine Learning Pipeline** for custom model training
- [ ] **Telemedicine Integration** with video consultation
- [ ] **Multi-language Support** for global accessibility
- [ ] **Blockchain Integration** for secure record keeping
- [ ] **IoT Device Integration** for real-time health monitoring

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Test on multiple Python versions

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This application is designed for educational and research purposes. Always consult with qualified healthcare professionals for medical decisions. The AI-generated diagnoses should be used as supplementary information only and not as a replacement for professional medical advice.

---

## 📞 Support & Contact

- 🐛 **Bug Reports:** [Create an Issue](../../issues)
- 💡 **Feature Requests:** [Create an Issue](../../issues)
- 📖 **Documentation:** [Wiki Pages](../../wiki)
- 💬 **Discussions:** [GitHub Discussions](../../discussions)

---

<div align="center">

**Made with ❤️ for Healthcare Innovation**

*Empowering medical professionals with AI-driven diagnostic insights*

</div>
