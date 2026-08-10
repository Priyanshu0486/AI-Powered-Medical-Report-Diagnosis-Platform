# MongoDB Migration Helper Script for Medical Diagnosis System
# Usage: .\migrate.ps1 [action]
# Actions: init, migrate, rollback, status, seed, backup

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("init", "migrate", "rollback", "status", "seed", "backup")]
    [string]$Action
)

function Show-Usage {
    Write-Host "Usage: .\migrate.ps1 [action]" -ForegroundColor Yellow
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  init     - Initialize database" -ForegroundColor Green
    Write-Host "  migrate  - Run all migrations" -ForegroundColor Green  
    Write-Host "  status   - Check migration status" -ForegroundColor Green
    Write-Host "  seed     - Add sample data" -ForegroundColor Green
    Write-Host "  backup   - Create database backup" -ForegroundColor Green
    Write-Host "  rollback - Rollback database (WARNING: DESTRUCTIVE)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\migrate.ps1 init" -ForegroundColor White
    Write-Host "  .\migrate.ps1 migrate" -ForegroundColor White
    Write-Host "  .\migrate.ps1 status" -ForegroundColor White
}

function Test-Prerequisites {
    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>$null
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python and try again" -ForegroundColor Yellow
        exit 1
    }

    # Check if migration script exists
    if (-not (Test-Path "scripts/migrate_db.py")) {
        Write-Host "❌ ERROR: migrate_db.py not found in current directory" -ForegroundColor Red
        Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
        exit 1
    }

    # Check if .env file exists
    if (-not (Test-Path ".env")) {
        Write-Host "⚠️  WARNING: .env file not found" -ForegroundColor Yellow
        Write-Host "Please ensure MongoDB connection details are properly configured" -ForegroundColor Yellow
        Write-Host ""
    }

    # Install requirements if needed
    if (Test-Path "migration_requirements.txt") {
        Write-Host "📦 Installing migration requirements..." -ForegroundColor Cyan
        try {
            pip install -r migration_requirements.txt | Out-Null
            Write-Host "✅ Requirements installed successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  WARNING: Failed to install some requirements" -ForegroundColor Yellow
            Write-Host "Please manually install: pymongo python-dotenv" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "⚠️  WARNING: migration_requirements.txt not found" -ForegroundColor Yellow
    }
}

function Invoke-Migration {
    param([string]$MigrationAction)
    
    Write-Host "🚀 Running migration: $MigrationAction" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        # Special handling for rollback action
        if ($MigrationAction -eq "rollback") {
            Write-Host "⚠️  WARNING: This will delete all data!" -ForegroundColor Red
            $confirm = Read-Host "Are you sure you want to proceed? (yes/no)"
            if ($confirm -ne "yes") {
                Write-Host "🚫 Migration cancelled" -ForegroundColor Yellow
                return
            }
        }
        
        # Run the migration
        $result = python scripts/migrate_db.py --action $MigrationAction
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Migration completed successfully!" -ForegroundColor Green
            
            # Show next steps based on action
            switch ($MigrationAction) {
                "init" {
                    Write-Host ""
                    Write-Host "Next steps:" -ForegroundColor Cyan
                    Write-Host "  .\migrate.ps1 seed    - Add sample data for testing" -ForegroundColor White
                    Write-Host "  .\migrate.ps1 status  - Check migration status" -ForegroundColor White
                }
                "seed" {
                    Write-Host ""
                    Write-Host "Sample data added! You can now:" -ForegroundColor Cyan
                    Write-Host "  - Login as admin/admin123" -ForegroundColor White
                    Write-Host "  - Login as doctor1/doctor123" -ForegroundColor White  
                    Write-Host "  - Login as patient1/patient123" -ForegroundColor White
                }
                "backup" {
                    Write-Host ""
                    Write-Host "Backup created successfully!" -ForegroundColor Cyan
                }
            }
        }
        else {
            Write-Host ""
            Write-Host "❌ Migration failed! Check the error messages above." -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host ""
        Write-Host "❌ Migration failed with error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Main execution
Write-Host "🏥 Medical Diagnosis System - Database Migration" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

# Test prerequisites
Test-Prerequisites

# Run migration
Invoke-Migration -MigrationAction $Action