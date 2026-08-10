#!/usr/bin/env pwsh
# MongoDB Schema Seeding PowerShell Script
# Medical Report Diagnosis System

function Show-Menu {
    Write-Host "`n================================" -ForegroundColor Cyan
    Write-Host "MongoDB Schema Seeding Utility" -ForegroundColor Cyan
    Write-Host "================================`n" -ForegroundColor Cyan
    
    Write-Host "Select an action:" -ForegroundColor Yellow
    Write-Host "1. Create new schemas with validation"
    Write-Host "2. Update existing schemas"
    Write-Host "3. Validate existing schemas"
    Write-Host "4. Drop schema validations"
    Write-Host "5. Show schema information"
    Write-Host "6. Exit`n"
}

function Test-Prerequisites {
    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
        exit 1
    }
    
    # Check if .env file exists
    if (-not (Test-Path ".env")) {
        Write-Host "❌ Error: .env file not found" -ForegroundColor Red
        Write-Host "Please create .env file with MONGO_URI and DB_NAME" -ForegroundColor Yellow
        exit 1
    }
    
    # Check if seed_schemas.py exists
    if (-not (Test-Path "scripts/seed_schemas.py")) {
        Write-Host "❌ Error: scripts/seed_schemas.py not found" -ForegroundColor Red
        exit 1
    }
}

# Main script
Clear-Host
Test-Prerequisites

while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-6)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nCreating schemas with validation...`n" -ForegroundColor Cyan
            python scripts/seed_schemas.py --action create
        }
        "2" {
            Write-Host "`nUpdating existing schemas...`n" -ForegroundColor Cyan
            python scripts/seed_schemas.py --action update
        }
        "3" {
            Write-Host "`nValidating existing schemas...`n" -ForegroundColor Cyan
            python scripts/seed_schemas.py --action validate
        }
        "4" {
            Write-Host "`nDropping schema validations...`n" -ForegroundColor Cyan
            python scripts/seed_schemas.py --action drop
        }
        "5" {
            Write-Host "`n" -ForegroundColor Cyan
            python scripts/seed_schemas.py --action info
        }
        "6" {
            Write-Host "`nGoodbye!`n" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "`n❌ Invalid choice, please try again`n" -ForegroundColor Red
        }
    }
    
    Write-Host "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
