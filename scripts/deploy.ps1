# Medical Report Diagnosis - PowerShell Deployment Script
# For Windows users

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "development", "prod", "production", "status", "logs", "stop", "clean", "test", "help")]
    [string]$Command = "help"
)

# Colors for output
function Write-ColorOutput([ConsoleColor]$ForegroundColor, [string]$Message) {
    $previousColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $Host.UI.RawUI.ForegroundColor = $previousColor
}

function Print-Step([string]$Message) {
    Write-ColorOutput Blue "📋 $Message"
}

function Print-Success([string]$Message) {
    Write-ColorOutput Green "✅ $Message"
}

function Print-Warning([string]$Message) {
    Write-ColorOutput Yellow "⚠️  $Message"
}

function Print-Error([string]$Message) {
    Write-ColorOutput Red "❌ $Message"
}

# Check if Docker is installed
function Test-DockerInstallation {
    Print-Step "Checking Docker installation..."
    
    try {
        $dockerVersion = docker --version 2>$null
        $composeVersion = docker-compose --version 2>$null
        
        if (-not $dockerVersion) {
            Print-Error "Docker is not installed. Please install Docker Desktop."
            exit 1
        }
        
        if (-not $composeVersion) {
            Print-Error "Docker Compose is not installed. Please install Docker Compose."
            exit 1
        }
        
        Print-Success "Docker and Docker Compose are installed"
    }
    catch {
        Print-Error "Failed to check Docker installation: $_"
        exit 1
    }
}

# Check environment file
function Test-EnvironmentFile {
    Print-Step "Checking environment configuration..."
    
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Print-Warning ".env file not found. Copying from .env.example"
            Copy-Item ".env.example" ".env"
            Print-Warning "Please edit .env file with your configuration before continuing"
            exit 1
        } else {
            Print-Error ".env file not found and no .env.example available"
            exit 1
        }
    }
    Print-Success "Environment file found"
}

# Create necessary directories
function New-RequiredDirectories {
    Print-Step "Creating necessary directories..."
    
    $directories = @("uploaded_reports", "logs", "uploaded_dir", "nginx\ssl")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Print-Success "Directories created"
}

# Start services
function Start-Services([string]$Environment) {
    Print-Step "Starting services in $Environment mode..."
    
    switch ($Environment) {
        { $_ -in @("development", "dev") } {
            docker-compose up --build -d
            if ($LASTEXITCODE -ne 0) {
                Print-Error "Failed to start development services"
                exit 1
            }
        }
        { $_ -in @("production", "prod") } {
            if (-not (Test-Path ".env.prod")) {
                Print-Error "Production environment file (.env.prod) not found"
                exit 1
            }
            docker-compose -f docker-compose.prod.yml up --build -d
            if ($LASTEXITCODE -ne 0) {
                Print-Error "Failed to start production services"
                exit 1
            }
        }
        default {
            Print-Error "Unknown environment type: $Environment"
            Print-Warning "Use: dev, development, prod, or production"
            exit 1
        }
    }
    
    Print-Success "Services started successfully"
}

# Show service status
function Show-ServiceStatus {
    Print-Step "Service Status:"
    docker-compose ps
    
    Write-Output ""
    Print-Step "Recent logs (last 10 lines):"
    docker-compose logs --tail=10
}

# Test services
function Test-Services {
    Print-Step "Testing service endpoints..."
    
    # Wait for services to be ready
    Start-Sleep -Seconds 10
    
    # Test backend health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Print-Success "Backend API is healthy"
        }
    }
    catch {
        Print-Warning "Backend API health check failed"
    }
    
    # Test frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Print-Success "Frontend is accessible"
        }
    }
    catch {
        Print-Warning "Frontend accessibility check failed"
    }
}

# Main deployment function
function Start-Deployment([string]$Environment) {
    Test-DockerInstallation
    Test-EnvironmentFile
    New-RequiredDirectories
    Start-Services $Environment
    Show-ServiceStatus
    Test-Services
    
    Write-Output ""
    Print-Success "🎉 Deployment completed successfully!"
    Write-Output ""
    Write-Output "📋 Access your application:"
    Write-Output "   🔗 Backend API: http://localhost:8000"
    Write-Output "   📖 API Docs: http://localhost:8000/docs"
    Write-Output "   🖥️  Frontend: http://localhost:8501"
    Write-Output ""
    Write-Output "📋 Useful commands:"
    Write-Output "   📊 View logs: docker-compose logs -f"
    Write-Output "   🔄 Restart: docker-compose restart"
    Write-Output "   🛑 Stop: docker-compose down"
    Write-Output "   🧹 Clean: docker-compose down -v"
}

# Handle script commands
switch ($Command) {
    { $_ -in @("dev", "development") } {
        Start-Deployment "development"
    }
    { $_ -in @("prod", "production") } {
        Start-Deployment "production"
    }
    "status" {
        Show-ServiceStatus
    }
    "logs" {
        docker-compose logs -f
    }
    "stop" {
        Print-Step "Stopping services..."
        docker-compose down
        Print-Success "Services stopped"
    }
    "clean" {
        Print-Step "Stopping and cleaning up..."
        docker-compose down -v
        docker system prune -f
        Print-Success "Cleanup completed"
    }
    "test" {
        Test-Services
    }
    "help" {
        Write-ColorOutput Blue "🏥 Medical Report Diagnosis - PowerShell Deployment Script"
        Write-Output ""
        Write-Output "Usage: .\deploy.ps1 [command]"
        Write-Output ""
        Write-Output "Commands:"
        Write-Output "  dev, development  Deploy in development mode"
        Write-Output "  prod, production  Deploy in production mode"
        Write-Output "  status           Show service status"
        Write-Output "  logs             Show service logs"
        Write-Output "  stop             Stop all services"
        Write-Output "  clean            Stop services and clean up"
        Write-Output "  test             Test service endpoints"
        Write-Output "  help             Show this help message"
        Write-Output ""
        Write-Output "Examples:"
        Write-Output "  .\deploy.ps1 dev           # Start development environment"
        Write-Output "  .\deploy.ps1 prod          # Start production environment"
        Write-Output "  .\deploy.ps1 logs          # View logs"
        Write-Output "  .\deploy.ps1 stop          # Stop services"
    }
    default {
        Write-ColorOutput Red "Unknown command: $Command"
        Write-Output "Use '.\deploy.ps1 help' for available commands"
    }
}