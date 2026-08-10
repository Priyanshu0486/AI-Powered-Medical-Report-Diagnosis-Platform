#!/usr/bin/env python3
"""
Comprehensive Service & Model Verification Script
Checks all services, models, APIs, and dependencies for the Medical Diagnosis System
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str, char: str = "="):
    """Print formatted header"""
    print(f"\n{Colors.CYAN}{char * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{char * 70}{Colors.RESET}")

def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'─' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}► {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'─' * 70}{Colors.RESET}")

def print_result(service: str, status: bool, message: str = "", details: str = ""):
    """Print formatted test result"""
    icon = f"{Colors.GREEN}✅{Colors.RESET}" if status else f"{Colors.RED}❌{Colors.RESET}"
    print(f"\n{icon} {Colors.BOLD}{service}{Colors.RESET}")
    if message:
        color = Colors.GREEN if status else Colors.RED
        print(f"   {color}{message}{Colors.RESET}")
    if details:
        print(f"   {Colors.YELLOW}{details}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

class ServiceVerifier:
    def __init__(self):
        self.results = {}
        self.model_results = {}
        self.dependency_results = {}
        
    def verify_mongodb(self) -> Tuple[bool, str, str]:
        """Verify MongoDB connection and collections"""
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
            
            mongo_uri = os.getenv("MONGO_URI")
            db_name = os.getenv("DB_NAME", "MedicalRag")
            
            if not mongo_uri:
                return False, "MONGO_URI not found in .env", ""
            
            print(f"   🔗 URI: {mongo_uri[:30]}...{mongo_uri[-30:]}")
            print(f"   📁 Database: {db_name}")
            print(f"   🔄 Connecting...")
            
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            
            db = client[db_name]
            collections = db.list_collection_names()
            
            # Check required collections
            required_collections = ["users", "reports", "diagnosis_history"]
            missing = [c for c in required_collections if c not in collections]
            
            stats = db.command("dbStats")
            size_mb = stats.get('dataSize', 0) / (1024 * 1024)
            
            details = f"Collections: {len(collections)} | Size: {size_mb:.2f} MB"
            
            if missing:
                details += f"\n   ⚠️  Missing collections: {', '.join(missing)}"
                print_warning(f"Missing collections: {', '.join(missing)}")
                print_info("Run: python seed_schemas.py --action create")
            
            # Check indexes
            print(f"   📊 Checking indexes...")
            for coll_name in collections:
                coll = db[coll_name]
                indexes = list(coll.list_indexes())
                print(f"      • {coll_name}: {len(indexes)} indexes")
            
            client.close()
            return True, f"Connected to {db_name}", details
            
        except OperationFailure as e:
            return False, "Authentication failed - Invalid credentials", str(e)
        except ConnectionFailure:
            return False, "Cannot reach MongoDB server", ""
        except ServerSelectionTimeoutError:
            return False, "Connection timeout - Check internet", ""
        except Exception as e:
            return False, f"Error: {str(e)}", ""
    
    def verify_google_ai(self) -> Tuple[bool, str, str]:
        """Verify Google AI and embedding model"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                return False, "GOOGLE_API_KEY not found in .env", ""
            
            print(f"   🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
            print(f"   🔄 Testing API...")
            
            genai.configure(api_key=api_key)
            
            # Test embedding model (used in your app)
            print(f"   📦 Testing embedding model...")
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            
            # Test embedding
            test_embedding = embed_model.embed_query("test")
            embedding_dim = len(test_embedding)
            
            return True, "Google AI API working", f"Embedding model: embedding-001 | Dimension: {embedding_dim}"
            
        except ImportError as e:
            missing_pkg = str(e).split("'")[1] if "'" in str(e) else "package"
            return False, f"Missing package: {missing_pkg}", "Install: pip install google-generativeai langchain-google-genai"
        except Exception as e:
            error_str = str(e)
            if "API key not valid" in error_str or "403" in error_str:
                return False, "Invalid API key", "Verify at: https://makersuite.google.com/app/apikey"
            return False, f"Error: {error_str[:100]}", ""
    
    def verify_pinecone(self) -> Tuple[bool, str, str]:
        """Verify Pinecone connection and index"""
        try:
            from pinecone import Pinecone
            
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX_NAME", "rbac-diagnosis-index")
            env = os.getenv("PINECONE_ENV", "us-east-1")
            
            if not api_key:
                return False, "PINECONE_API_KEY not found in .env", ""
            
            print(f"   🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
            print(f"   📊 Index: {index_name}")
            print(f"   🌍 Environment: {env}")
            print(f"   🔄 Connecting...")
            
            pc = Pinecone(api_key=api_key)
            
            # List indexes
            indexes = pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            print(f"   📋 Found indexes: {', '.join(index_names) if index_names else 'None'}")
            
            if index_name not in index_names:
                return False, f"Index '{index_name}' not found", f"Available: {', '.join(index_names) if index_names else 'None'}\n   💡 Run server to auto-create or create manually"
            
            # Get index stats
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            
            total_vectors = stats.get('total_vector_count', 0)
            dimension = stats.get('dimension', 'N/A')
            
            return True, f"Index '{index_name}' ready", f"Vectors: {total_vectors} | Dimension: {dimension}"
            
        except ImportError:
            return False, "pinecone package not installed", "Install: pip install pinecone-client"
        except Exception as e:
            return False, f"Error: {str(e)[:100]}", ""
    
    def verify_groq(self) -> Tuple[bool, str, str]:
        """Verify Groq AI and LLM model"""
        try:
            from groq import Groq
            from langchain_groq import ChatGroq
            
            api_key = os.getenv("GROQ_API_KEY")
            
            if not api_key:
                return False, "GROQ_API_KEY not found in .env", ""
            
            print(f"   🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
            print(f"   🔄 Testing API...")
            
            # Test direct Groq client
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b-versatile",
                max_tokens=10
            )
            
            # Test LangChain integration (used in your app)
            print(f"   🔗 Testing LangChain integration...")
            llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", groq_api_key=api_key)
            test_response = llm.invoke("Hi")
            
            return True, "Groq AI working", f"Models: llama-3.3-70b-versatile, llama3-8b-8192 ✓"
            
        except ImportError as e:
            missing_pkg = str(e).split("'")[1] if "'" in str(e) else "groq"
            return False, f"Missing package: {missing_pkg}", "Install: pip install groq langchain-groq"
        except Exception as e:
            return False, f"Error: {str(e)[:100]}", ""
    
    def verify_api_server(self) -> Tuple[bool, str, str]:
        """Verify API server is running"""
        try:
            import requests
            
            api_url = os.getenv("API_URL", "http://localhost:8000")
            
            print(f"   🌐 URL: {api_url}")
            print(f"   🔄 Checking...")
            
            # Try root endpoint
            try:
                response = requests.get(api_url, timeout=3)
                status_code = response.status_code
            except:
                # Try /health endpoint (from main.py)
                response = requests.get(f"{api_url}/health", timeout=3)
                status_code = response.status_code
            
            if status_code == 200:
                # Check available endpoints
                try:
                    docs_response = requests.get(f"{api_url}/docs", timeout=2)
                    has_docs = docs_response.status_code == 200
                except:
                    has_docs = False
                
                return True, f"Server running on {api_url}", f"Docs: {'Available' if has_docs else 'N/A'} at {api_url}/docs"
            else:
                return False, f"Server responded with {status_code}", ""
            
        except ImportError:
            return False, "requests package not installed", "Install: pip install requests"
        except Exception:
            return False, "Server not running", "Start: uvicorn server.main:app --reload"
    
    def verify_dependencies(self) -> Dict[str, bool]:
        """Verify all Python dependencies"""
        dependencies = {
            "fastapi": "FastAPI framework",
            "uvicorn": "ASGI server",
            "pymongo": "MongoDB driver",
            "python-dotenv": "Environment variables (imported as 'dotenv')",
            "pinecone": "Pinecone client (imported as 'pinecone')",
            "langchain": "LangChain framework",
            "langchain-groq": "LangChain Groq integration (imported as 'langchain_groq')",
            "langchain-google-genai": "LangChain Google AI (imported as 'langchain_google_genai')",
            "langchain-community": "LangChain community (imported as 'langchain_community')",
            "google-generativeai": "Google AI SDK (imported as 'google.generativeai')",
            "groq": "Groq SDK",
            "pypdf": "PDF processing",
            "PyPDF2": "PDF processing (imported as 'PyPDF2')",
            "passlib": "Password hashing",
            "streamlit": "Streamlit UI",
            "requests": "HTTP requests",
            "tqdm": "Progress bars"
        }
        
        results = {}
        
        for package, description in dependencies.items():
            # Handle special import names
            import_name = package
            if package == "python-dotenv":
                import_name = "dotenv"
            elif package == "google-generativeai":
                import_name = "google.generativeai"
            elif package == "langchain-groq":
                import_name = "langchain_groq"
            elif package == "langchain-google-genai":
                import_name = "langchain_google_genai"
            elif package == "langchain-community":
                import_name = "langchain_community"
            
            try:
                __import__(import_name)
                results[package] = True
                print(f"   {Colors.GREEN}✓{Colors.RESET} {package:30} - {description}")
            except ImportError:
                results[package] = False
                print(f"   {Colors.RED}✗{Colors.RESET} {package:30} - {description} {Colors.RED}(MISSING){Colors.RESET}")
        
        return results
    
    def verify_file_structure(self) -> Dict[str, bool]:
        """Verify required files and directories exist"""
        required_files = {
            ".env": "Environment configuration",
            "requirements.txt": "Python dependencies",
            "server/main.py": "FastAPI application",
            "server/config/db.py": "Database configuration",
            "server/auth/route.py": "Authentication routes",
            "server/reports/route.py": "Reports routes",
            "server/reports/vectorstore.py": "Vector store logic",
            "server/diagnosis/route.py": "Diagnosis routes",
            "server/diagnosis/query.py": "RAG query logic",
            "server/models/db_models.py": "Database models",
            "client/app.py": "Streamlit client",
            "scripts/migrate_db.py": "Database migration script",
            "scripts/seed_schemas.py": "Schema seeding script"
        }
        
        results = {}
        
        for file_path, description in required_files.items():
            exists = os.path.exists(file_path)
            results[file_path] = exists
            
            icon = f"{Colors.GREEN}✓{Colors.RESET}" if exists else f"{Colors.RED}✗{Colors.RESET}"
            print(f"   {icon} {file_path:40} - {description}")
        
        return results
    
    def verify_env_variables(self) -> Dict[str, bool]:
        """Verify required environment variables"""
        required_vars = {
            "MONGO_URI": "MongoDB connection string",
            "DB_NAME": "Database name",
            "GOOGLE_API_KEY": "Google AI API key",
            "PINECONE_API_KEY": "Pinecone API key",
            "PINECONE_ENV": "Pinecone environment",
            "PINECONE_INDEX_NAME": "Pinecone index name",
            "GROQ_API_KEY": "Groq API key",
            "API_URL": "API server URL",
            "UPLOAD_DIR": "Upload directory path"
        }
        
        results = {}
        
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            exists = value is not None and value != ""
            results[var_name] = exists
            
            icon = f"{Colors.GREEN}✓{Colors.RESET}" if exists else f"{Colors.RED}✗{Colors.RESET}"
            
            if exists:
                # Mask sensitive values
                if "KEY" in var_name or "URI" in var_name:
                    display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
                else:
                    display_value = value
                print(f"   {icon} {var_name:25} = {display_value}")
            else:
                print(f"   {icon} {var_name:25} {Colors.RED}(MISSING){Colors.RESET} - {description}")
        
        return results
    
    def run_all_checks(self):
        """Run all verification checks"""
        print_header("🔍 COMPREHENSIVE SERVICE & MODEL VERIFICATION", "🔍")
        print(f"{Colors.CYAN}   Medical Report Diagnosis System{Colors.RESET}")
        print(f"{Colors.CYAN}   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        
        # Check .env file
        if not os.path.exists(".env"):
            print(f"\n{Colors.RED}❌ CRITICAL: .env file not found!{Colors.RESET}")
            print(f"{Colors.YELLOW}   Create .env file with required configuration{Colors.RESET}")
            return
        
        print(f"\n{Colors.GREEN}✅ Found .env file{Colors.RESET}")
        
        # 1. Environment Variables
        print_section("1️⃣  Environment Variables")
        env_results = self.verify_env_variables()
        
        # 2. File Structure
        print_section("2️⃣  File Structure")
        file_results = self.verify_file_structure()
        
        # 3. Python Dependencies
        print_section("3️⃣  Python Dependencies")
        dep_results = self.verify_dependencies()
        
        # 4. Service Connections
        print_section("4️⃣  Service Connections")
        
        # MongoDB
        print(f"\n{Colors.BOLD}🗄️  MongoDB Database{Colors.RESET}")
        status, msg, details = self.verify_mongodb()
        print_result("MongoDB", status, msg, details)
        self.results["MongoDB"] = status
        
        # Google AI
        print(f"\n{Colors.BOLD}🤖 Google AI (Embeddings){Colors.RESET}")
        status, msg, details = self.verify_google_ai()
        print_result("Google AI", status, msg, details)
        self.results["Google AI"] = status
        
        # Pinecone
        print(f"\n{Colors.BOLD}📊 Pinecone (Vector DB){Colors.RESET}")
        status, msg, details = self.verify_pinecone()
        print_result("Pinecone", status, msg, details)
        self.results["Pinecone"] = status
        
        # Groq
        print(f"\n{Colors.BOLD}🚀 Groq AI (LLM){Colors.RESET}")
        status, msg, details = self.verify_groq()
        print_result("Groq AI", status, msg, details)
        self.results["Groq AI"] = status
        
        # API Server
        print(f"\n{Colors.BOLD}🌐 API Server{Colors.RESET}")
        status, msg, details = self.verify_api_server()
        print_result("API Server", status, msg, details)
        self.results["API Server"] = status
        
        # 5. Summary
        self.print_summary(env_results, file_results, dep_results)
    
    def print_summary(self, env_results, file_results, dep_results):
        """Print comprehensive summary"""
        print_header("📊 VERIFICATION SUMMARY", "=")
        
        # Service Status
        print(f"\n{Colors.BOLD}🔌 Service Status:{Colors.RESET}")
        for service, status in self.results.items():
            icon = f"{Colors.GREEN}✅{Colors.RESET}" if status else f"{Colors.RED}❌{Colors.RESET}"
            print(f"   {icon} {service}")
        
        # Statistics
        services_ok = sum(1 for v in self.results.values() if v)
        total_services = len(self.results)
        
        env_ok = sum(1 for v in env_results.values() if v)
        total_env = len(env_results)
        
        files_ok = sum(1 for v in file_results.values() if v)
        total_files = len(file_results)
        
        deps_ok = sum(1 for v in dep_results.values() if v)
        total_deps = len(dep_results)
        
        print(f"\n{Colors.BOLD}📈 Statistics:{Colors.RESET}")
        print(f"   Services:     {services_ok}/{total_services} connected")
        print(f"   Environment:  {env_ok}/{total_env} variables set")
        print(f"   Files:        {files_ok}/{total_files} exist")
        print(f"   Dependencies: {deps_ok}/{total_deps} installed")
        
        # Overall Status
        all_critical = services_ok >= 3  # MongoDB, Groq, at least one more
        
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        if all_critical and services_ok == total_services:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL SYSTEMS OPERATIONAL!{Colors.RESET}")
        elif all_critical:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SYSTEM PARTIALLY OPERATIONAL{Colors.RESET}")
            print(f"{Colors.YELLOW}   Some services need attention{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ CRITICAL SERVICES DOWN{Colors.RESET}")
            print(f"{Colors.RED}   Fix critical issues before running{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}💡 Recommendations:{Colors.RESET}")
        
        if not self.results.get("MongoDB", False):
            print(f"{Colors.YELLOW}   1. Fix MongoDB authentication - Reset password in Atlas{Colors.RESET}")
        
        if not self.results.get("Google AI", False):
            print(f"{Colors.YELLOW}   2. Verify Google AI API key at https://makersuite.google.com{Colors.RESET}")
        
        if not self.results.get("Pinecone", False):
            print(f"{Colors.YELLOW}   3. Start API server to auto-create Pinecone index{Colors.RESET}")
        
        if not self.results.get("API Server", False):
            print(f"{Colors.YELLOW}   4. Start API server: uvicorn server.main:app --reload{Colors.RESET}")
        
        missing_deps = [pkg for pkg, status in dep_results.items() if not status]
        if missing_deps:
            print(f"{Colors.YELLOW}   5. Install missing packages: pip install {' '.join(missing_deps)}{Colors.RESET}")
        
        print()


def main():
    """Main entry point"""
    try:
        verifier = ServiceVerifier()
        verifier.run_all_checks()
        
        # Return exit code based on critical services
        critical_services = ["MongoDB", "Groq AI"]
        critical_ok = all(verifier.results.get(s, False) for s in critical_services)
        
        return 0 if critical_ok else 1
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🚫 Verification interrupted by user{Colors.RESET}")
        return 1
    except Exception as e:
        print(f"\n\n{Colors.RED}💥 Unexpected error: {e}{Colors.RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
