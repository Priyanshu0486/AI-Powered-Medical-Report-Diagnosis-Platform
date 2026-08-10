@echo off
REM MongoDB Migration Helper Script for Medical Diagnosis System
REM Usage: migrate.bat [action]
REM Actions: init, migrate, rollback, status, seed, backup

setlocal

if "%1"=="" (
    echo Usage: migrate.bat [action]
    echo Actions: init, migrate, rollback, status, seed, backup
    echo.
    echo Examples:
    echo   migrate.bat init     - Initialize database
    echo   migrate.bat migrate  - Run all migrations  
    echo   migrate.bat status   - Check migration status
    echo   migrate.bat seed     - Add sample data
    echo   migrate.bat backup   - Create database backup
    echo   migrate.bat rollback - Rollback database ^(WARNING: DESTRUCTIVE^)
    goto :eof
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    goto :eof
)

REM Check if migration script exists
if not exist "scripts\migrate_db.py" (
    echo ERROR: migrate_db.py not found in current directory
    echo Please run this script from the project root directory
    goto :eof
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please ensure MongoDB connection details are properly configured
    echo.
)

REM Install requirements if needed
if not exist "migration_requirements.txt" (
    echo WARNING: migration_requirements.txt not found
) else (
    echo Installing migration requirements...
    pip install -r migration_requirements.txt
    if errorlevel 1 (
        echo WARNING: Failed to install some requirements
        echo Please manually install: pymongo python-dotenv
        echo.
    )
)

REM Run migration command
echo Running migration: %1
echo.
python scripts/migrate_db.py --action %1

if errorlevel 1 (
    echo.
    echo Migration failed! Check the error messages above.
) else (
    echo.
    echo Migration completed successfully!
)

endlocal