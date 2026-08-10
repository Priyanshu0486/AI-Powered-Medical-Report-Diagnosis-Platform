#!/usr/bin/env python3
"""Quick Google Gemini AI Connection Test"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Google Gemini AI Connection...")
print("=" * 60)

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        exit(1)
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"🔄 Configuring API...\n")
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Try to list available models
    print("📋 Checking available models...")
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
                print(f"   • {m.name}")
        
        if not models:
            print("   ⚠️  No models available")
    except Exception as e:
        print(f"   ℹ️  Could not list models: {str(e)[:50]}")
    
    # Test with a simple generation (try Gemini 2.0 models only)
    print(f"\n🤖 Testing text generation...")
    
    test_models = [
        "gemini-2.0-flash",
        "gemini-2.0-pro"
    ]
    
    success = False
    working_model = None
    
    for model_name in test_models:
        try:
            print(f"   Trying {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, respond with just 'Hi'")
            
            if response and response.text:
                print(f"✅ Success!")
                working_model = model_name
                success = True
                break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"❌ Quota exceeded")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"❌ Not available")
            else:
                print(f"❌ Error: {error_msg[:30]}")
    
    if success:
        print(f"\n✅ Google Gemini AI is working!")
        print(f"🎯 Working Model: {working_model}")
        
        # Test embedding model used in your app
        print(f"\n📦 Testing embedding model...")
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            test_embedding = embed_model.embed_query("test")
            print(f"✅ Embeddings working!")
            print(f"   Dimension: {len(test_embedding)}")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"❌ Embeddings - Quota exceeded")
                print(f"   💡 Your free tier quota has been reached")
                print(f"   💡 Solution: Use HuggingFace embeddings instead")
            else:
                print(f"❌ Embeddings error: {error_msg[:60]}")
        
    else:
        print(f"\n❌ Could not connect to any Gemini model")
        print(f"\n💡 Possible issues:")
        print(f"   1. API quota exceeded (most common)")
        print(f"   2. Invalid API key")
        print(f"   3. API access not enabled")
        
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 Gemini API connection successful!")
    else:
        print("⚠️  Gemini API connection failed - See solutions below")
        print("\n💡 Solutions:")
        print("   1. Check quota: https://makersuite.google.com/app/apikey")
        print("   2. Wait for quota reset (usually 24 hours)")
        print("   3. Use HuggingFace embeddings instead (recommended):")
        print("      pip install sentence-transformers langchain-huggingface")
        print("      Then update your code to use HuggingFaceEmbeddings")
    
except ImportError as e:
    print("❌ Required package not installed")
    print(f"   Error: {str(e)}")
    print("\n💡 Install with:")
    print("   pip install google-generativeai langchain-google-genai")
    
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    print("\n💡 Check:")
    print("   1. GOOGLE_API_KEY is set in .env")
    print("   2. API key is valid")
    print("   3. Internet connection is working")
