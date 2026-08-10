@echo off
REM MongoDB Schema Seeding Batch Script for Windows
REM Medical Report Diagnosis System

echo ================================
echo MongoDB Schema Seeding Utility
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found
    echo Please create .env file with MONGO_URI and DB_NAME
    pause
    exit /b 1
)

REM Show menu
:menu
echo.
echo Select an action:
echo 1. Create new schemas with validation
echo 2. Update existing schemas
echo 3. Validate existing schemas
echo 4. Drop schema validations
echo 5. Show schema information
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto create
if "%choice%"=="2" goto update
if "%choice%"=="3" goto validate
if "%choice%"=="4" goto drop
if "%choice%"=="5" goto info
if "%choice%"=="6" goto end
echo Invalid choice, please try again
goto menu

:create
echo.
echo Creating schemas with validation...
python scripts/seed_schemas.py --action create
goto menu

:update
echo.
echo Updating existing schemas...
python scripts/seed_schemas.py --action update
goto menu

:validate
echo.
echo Validating existing schemas...
python scripts/seed_schemas.py --action validate
goto menu

:drop
echo.
echo Dropping schema validations...
python scripts/seed_schemas.py --action drop
goto menu

:info
echo.
python scripts/seed_schemas.py --action info
goto menu

:end
echo.
echo Goodbye!
pause
