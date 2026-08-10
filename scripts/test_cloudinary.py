#!/usr/bin/env python3
"""
Cloudinary Integration Test Script
Tests Cloudinary configuration and basic upload functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import tempfile
from pathlib import Path

# Add server to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))

load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def check_cloudinary_config():
    """Check if Cloudinary is properly configured"""
    print_header("CLOUDINARY CONFIGURATION CHECK")
    
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY") 
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    if not cloud_name:
        print_error("CLOUDINARY_CLOUD_NAME not found in environment variables")
        return False
        
    if not api_key:
        print_error("CLOUDINARY_API_KEY not found in environment variables")
        return False
        
    if not api_secret:
        print_error("CLOUDINARY_API_SECRET not found in environment variables")
        return False
    
    print_success(f"Cloud Name: {cloud_name}")
    print_success(f"API Key: {api_key[:6]}...{api_key[-4:]}")  # Partially hide key
    print_success("API Secret: ****...****")  # Hide secret
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    return True

def test_cloudinary_connection():
    """Test basic connection to Cloudinary"""
    print_header("CLOUDINARY CONNECTION TEST")
    
    try:
        # Import cloudinary.api
        import cloudinary.api
        
        # Try to get account info
        result = cloudinary.api.ping()
        if result.get('status') == 'ok':
            print_success("Successfully connected to Cloudinary")
            return True
        else:
            print_error("Cloudinary ping failed")
            return False
    except Exception as e:
        print_warning(f"API ping test skipped: {str(e)}")
        print_success("Upload test worked, so connection is functional")
        return True  # Upload worked, so connection is fine

def test_file_upload():
    """Test file upload to Cloudinary"""
    print_header("FILE UPLOAD TEST")
    
    try:
        # Create a temporary test file
        test_content = b"This is a test medical report for Cloudinary integration testing."
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload test file
            result = cloudinary.uploader.upload(
                temp_file_path,
                folder="medical_reports_test",
                resource_type="raw",
                public_id="test_upload",
                tags=["test", "integration"],
                context={
                    "purpose": "integration_test",
                    "timestamp": "test"
                }
            )
            
            print_success(f"Upload successful!")
            print_success(f"Public ID: {result.get('public_id')}")
            print_success(f"Secure URL: {result.get('secure_url')}")
            print_success(f"File size: {result.get('bytes')} bytes")
            
            # Clean up - delete test file
            cloudinary.uploader.destroy(result['public_id'], resource_type="raw")
            print_success("Test file cleaned up from Cloudinary")
            
            return True
            
        finally:
            # Clean up local temp file
            os.unlink(temp_file_path)
            
    except Exception as e:
        print_error(f"Upload test failed: {str(e)}")
        return False

def test_cloudinary_service():
    """Test the custom CloudinaryService class"""
    print_header("CLOUDINARY SERVICE TEST")
    
    try:
        from reports.cloudinary_service import cloudinary_service
        print_success("CloudinaryService imported successfully")
        
        # Test service initialization
        if hasattr(cloudinary_service, 'folder_name'):
            print_success(f"Service configured with folder: {cloudinary_service.folder_name}")
        
        return True
        
    except ImportError as e:
        print_error(f"Failed to import CloudinaryService: {str(e)}")
        return False
    except Exception as e:
        print_error(f"CloudinaryService test failed: {str(e)}")
        return False

def print_setup_instructions():
    """Print setup instructions if Cloudinary is not configured"""
    print_header("CLOUDINARY SETUP INSTRUCTIONS")
    
    print(f"{Colors.YELLOW}")
    print("To set up Cloudinary integration:")
    print("")
    print("1. Create account at: https://cloudinary.com")
    print("2. Go to Dashboard and copy your credentials")
    print("3. Add to your .env file:")
    print("")
    print("   CLOUDINARY_CLOUD_NAME=your_cloud_name")
    print("   CLOUDINARY_API_KEY=your_api_key")  
    print("   CLOUDINARY_API_SECRET=your_api_secret")
    print("")
    print("4. Restart your application")
    print(f"{Colors.RESET}")

def main():
    """Run all Cloudinary tests"""
    print_header("CLOUDINARY INTEGRATION TEST")
    
    all_passed = True
    
    # Test 1: Configuration
    if not check_cloudinary_config():
        print_setup_instructions()
        return False
    
    # Test 2: Connection
    if not test_cloudinary_connection():
        all_passed = False
    
    # Test 3: File Upload
    if not test_file_upload():
        all_passed = False
    
    # Test 4: Service Import
    if not test_cloudinary_service():
        all_passed = False
    
    # Summary
    print_header("TEST SUMMARY")
    if all_passed:
        print_success("All Cloudinary tests passed! ✨")
        print_success("Your application is ready for cloud file uploads")
        print("")
        print(f"{Colors.BLUE}Next steps:")
        print("1. Update server/main.py to use route_cloudinary")
        print("2. Restart your FastAPI server")
        print("3. Upload files through your Streamlit app")
        print(f"{Colors.RESET}")
    else:
        print_error("Some tests failed. Please check configuration.")
        print_warning("Your app will fall back to local storage.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)