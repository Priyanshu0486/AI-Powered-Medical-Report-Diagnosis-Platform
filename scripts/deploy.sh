#!/bin/bash

# Medical Report Diagnosis - Deployment Script
set -e

echo "🏥 Medical Report Diagnosis - Docker Deployment"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    print_step "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check environment file
check_env_file() {
    print_step "Checking environment configuration..."
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_warning ".env file not found. Copying from .env.example"
            cp .env.example .env
            print_warning "Please edit .env file with your configuration before continuing"
            exit 1
        else
            print_error ".env file not found and no .env.example available"
            exit 1
        fi
    fi
    print_success "Environment file found"
}

# Create necessary directories
create_directories() {
    print_step "Creating necessary directories..."
    mkdir -p uploaded_reports
    mkdir -p logs
    mkdir -p uploaded_dir
    mkdir -p nginx/ssl
    print_success "Directories created"
}

# Build and start services
start_services() {
    local env_type=${1:-development}
    
    print_step "Starting services in $env_type mode..."
    
    case $env_type in
        "development"|"dev")
            docker-compose up --build -d
            ;;
        "production"|"prod")
            if [ ! -f .env.prod ]; then
                print_error "Production environment file (.env.prod) not found"
                exit 1
            fi
            docker-compose -f docker-compose.prod.yml up --build -d
            ;;
        *)
            print_error "Unknown environment type: $env_type"
            print_warning "Use: dev, development, prod, or production"
            exit 1
            ;;
    esac
    
    print_success "Services started successfully"
}

# Show service status
show_status() {
    print_step "Service Status:"
    docker-compose ps
    
    print_step "Service Logs (last 10 lines):"
    docker-compose logs --tail=10
}

# Test services
test_services() {
    print_step "Testing service endpoints..."
    
    # Wait for services to be ready
    sleep 10
    
    # Test backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend API is healthy"
    else
        print_warning "Backend API health check failed"
    fi
    
    # Test frontend
    if curl -f http://localhost:8501 &> /dev/null; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend accessibility check failed"
    fi
}

# Main deployment function
deploy() {
    local env_type=${1:-development}
    
    check_docker
    check_env_file
    create_directories
    start_services $env_type
    show_status
    test_services
    
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Access your application:"
    echo "   🔗 Backend API: http://localhost:8000"
    echo "   📖 API Docs: http://localhost:8000/docs"
    echo "   🖥️  Frontend: http://localhost:8501"
    echo ""
    echo "📋 Useful commands:"
    echo "   📊 View logs: docker-compose logs -f"
    echo "   🔄 Restart: docker-compose restart"
    echo "   🛑 Stop: docker-compose down"
    echo "   🧹 Clean: docker-compose down -v"
}

# Handle script arguments
case "${1:-help}" in
    "dev"|"development")
        deploy "development"
        ;;
    "prod"|"production")
        deploy "production"
        ;;
    "status")
        show_status
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "stop")
        print_step "Stopping services..."
        docker-compose down
        print_success "Services stopped"
        ;;
    "clean")
        print_step "Stopping and cleaning up..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup completed"
        ;;
    "test")
        test_services
        ;;
    "help"|*)
        echo "🏥 Medical Report Diagnosis - Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  dev, development  Deploy in development mode"
        echo "  prod, production  Deploy in production mode"
        echo "  status           Show service status"
        echo "  logs             Show service logs"
        echo "  stop             Stop all services"
        echo "  clean            Stop services and clean up"
        echo "  test             Test service endpoints"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 dev           # Start development environment"
        echo "  $0 prod          # Start production environment"
        echo "  $0 logs          # View logs"
        echo "  $0 stop          # Stop services"
        ;;
esac