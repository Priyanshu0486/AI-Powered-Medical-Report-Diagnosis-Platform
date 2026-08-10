#!/usr/bin/env pwsh
# Quick Fix Script for Medical Diagnosis System
# Applies all necessary fixes automatically

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Medical Diagnosis System - Quick Fix Utility" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# Step 1: Check Groq model fix
Write-Host "1️⃣  Checking Groq Model Configuration..." -ForegroundColor Yellow
$queryFile = "server/diagnosis/query.py"
$queryContent = Get-Content $queryFile -Raw

if ($queryContent -match "llama-3.1-8b-instant") {
    Write-Host "   ✅ Groq model already updated to llama-3.1-8b-instant" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Groq model needs manual update in $queryFile" -ForegroundColor Yellow
}

# Step 2: Check MongoDB connection
Write-Host "`n2️⃣  Checking MongoDB Configuration..." -ForegroundColor Yellow
$envFile = ".env"
$envContent = Get-Content $envFile -Raw

if ($envContent -match "MONGO_URI=.*mongodb\+srv://") {
    Write-Host "   ℹ️  MongoDB URI configured" -ForegroundColor Cyan
    Write-Host "   ⚠️  If authentication fails, reset password in MongoDB Atlas:" -ForegroundColor Yellow
    Write-Host "      → https://cloud.mongodb.com" -ForegroundColor Gray
    Write-Host "      → Database Access → Edit User → Edit Password" -ForegroundColor Gray
} else {
    Write-Host "   ❌ MongoDB URI not found in .env" -ForegroundColor Red
}

# Step 3: Check for alternative embeddings package
Write-Host "`n3️⃣  Checking Alternative Embeddings..." -ForegroundColor Yellow
try {
    $installed = pip list 2>&1 | Select-String "sentence-transformers"
    if ($installed) {
        Write-Host "   ✅ sentence-transformers already installed" -ForegroundColor Green
    } else {
        throw "Not installed"
    }
} catch {
    Write-Host "   ℹ️  sentence-transformers not installed (optional)" -ForegroundColor Cyan
    Write-Host "   💡 To use HuggingFace embeddings instead of Google AI:" -ForegroundColor Yellow
    Write-Host "      pip install sentence-transformers langchain-huggingface" -ForegroundColor Gray
}

# Step 4: Check if server is running
Write-Host "`n4️⃣  Checking API Server Status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ API Server is running on http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API Server is not running" -ForegroundColor Red
    Write-Host "   💡 Start with: uvicorn server.main:app --reload" -ForegroundColor Yellow
}

# Step 5: Summary and next steps
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  SUMMARY & NEXT STEPS" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "📋 Required Actions:`n" -ForegroundColor Yellow

Write-Host "   1. Fix MongoDB Password:" -ForegroundColor White
Write-Host "      • Go to: https://cloud.mongodb.com" -ForegroundColor Gray
Write-Host "      • Database Access → Edit User 'Pratyush' → Reset Password" -ForegroundColor Gray
Write-Host "      • Update .env with new password`n" -ForegroundColor Gray

Write-Host "   2. Fix Google AI Quota (Choose one option):" -ForegroundColor White
Write-Host "      Option A: Wait for quota reset (tomorrow)" -ForegroundColor Gray
Write-Host "      Option B: Use HuggingFace embeddings instead:" -ForegroundColor Gray
Write-Host "                pip install sentence-transformers langchain-huggingface" -ForegroundColor Gray
Write-Host "                Then edit server/reports/vectorstore.py`n" -ForegroundColor Gray

Write-Host "   3. Start API Server:" -ForegroundColor White
Write-Host "      uvicorn server.main:app --reload`n" -ForegroundColor Gray

Write-Host "   4. Verify Everything:" -ForegroundColor White
Write-Host "      python verify_all_services.py`n" -ForegroundColor Gray

Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "📖 For detailed instructions, see:" -ForegroundColor Cyan
Write-Host "   • SERVICE_FIX_GUIDE.md (comprehensive guide)" -ForegroundColor Gray
Write-Host "   • CONNECTION_TEST_REPORT.md (diagnostic report)`n" -ForegroundColor Gray

Write-Host "❓ Need help? Check the guides above for step-by-step instructions!`n" -ForegroundColor Yellow
