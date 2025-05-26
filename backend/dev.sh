#!/bin/bash

# rwanly Core ERP Backend Development Scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Activate virtual environment if it exists
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        log_info "Activating virtual environment..."
        source venv/bin/activate
    else
        log_warning "Virtual environment not found. Run ./setup.sh first."
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        log_warning "Please edit .env file with your database credentials"
    fi
}

# Main script logic
case "$1" in
    "setup")
        log_info "Setting up rwanly backend..."
        ./setup.sh
        ;;
    
    "install")
        log_info "Installing dependencies..."
        activate_venv
        pip install -r requirements.txt
        log_success "Dependencies installed!"
        ;;
    
    "dev")
        log_info "Starting development server..."
        activate_venv
        check_env
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    
    "start")
        log_info "Starting production server..."
        activate_venv
        check_env
        uvicorn main:app --host 0.0.0.0 --port 8000
        ;;
    
    "test")
        log_info "Running tests..."
        activate_venv
        pytest -v
        ;;
    
    "init-db")
        log_info "Initializing database..."
        activate_venv
        check_env
        python init_db.py
        ;;
    
    "migrate")
        log_info "Running database migrations..."
        activate_venv
        check_env
        alembic upgrade head
        ;;
    
    "migration")
        if [ -z "$2" ]; then
            log_error "Please provide a migration message: ./dev.sh migration 'Your message'"
            exit 1
        fi
        log_info "Creating new migration: $2"
        activate_venv
        check_env
        alembic revision --autogenerate -m "$2"
        ;;
    
    "shell")
        log_info "Starting Python shell with app context..."
        activate_venv
        check_env
        python -c "
from app.database import SessionLocal
from app.models import *
from app.crud import *
import os
print('rwanly Core ERP - Python Shell')
print('Available: SessionLocal, all models, all CRUD operations')
print('Example: db = SessionLocal(); users = user_crud.get_all(db)')
"
        python
        ;;
    
    "lint")
        log_info "Running code linting..."
        activate_venv
        flake8 app/ --max-line-length=100 --exclude=__pycache__,migrations
        ;;
    
    "format")
        log_info "Formatting code..."
        activate_venv
        black app/ --line-length=100
        ;;
    
    "clean")
        log_info "Cleaning up cache files..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "*.pyo" -delete 2>/dev/null || true
        find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        rm -f test.db 2>/dev/null || true
        log_success "Cache cleaned!"
        ;;
    
    "logs")
        log_info "Showing application logs..."
        if [ -f "app.log" ]; then
            tail -f app.log
        else
            log_warning "No log file found. Logs are printed to console in development mode."
        fi
        ;;
    
    "status")
        log_info "Backend Status Check"
        echo "===================="
        
        # Check Python
        if command -v python3 >/dev/null 2>&1; then
            log_success "Python 3: $(python3 --version)"
        else
            log_error "Python 3: Not found"
        fi
        
        # Check virtual environment
        if [ -d "venv" ]; then
            log_success "Virtual Environment: Found"
        else
            log_warning "Virtual Environment: Not found"
        fi
        
        # Check .env file
        if [ -f ".env" ]; then
            log_success "Environment File: Found"
        else
            log_warning "Environment File: Not found"
        fi
        
        # Check PostgreSQL
        if command -v psql >/dev/null 2>&1; then
            log_success "PostgreSQL: Available"
        else
            log_warning "PostgreSQL: Not found in PATH"
        fi
        
        # Check if server is running
        if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
            log_success "API Server: Running (http://localhost:8000)"
        else
            log_warning "API Server: Not running"
        fi
        ;;
    
    "help"|*)
        echo "rwanly Core ERP Backend - Development Commands"
        echo "=============================================="
        echo ""
        echo "Setup & Installation:"
        echo "  ./dev.sh setup         - Initial setup (creates venv, installs deps)"
        echo "  ./dev.sh install       - Install/update dependencies"
        echo ""
        echo "Development:"
        echo "  ./dev.sh dev           - Start development server with auto-reload"
        echo "  ./dev.sh start         - Start production server"
        echo "  ./dev.sh test          - Run tests"
        echo "  ./dev.sh shell         - Start Python shell with app context"
        echo ""
        echo "Database:"
        echo "  ./dev.sh init-db       - Initialize database with sample data"
        echo "  ./dev.sh migrate       - Run database migrations"
        echo "  ./dev.sh migration 'msg' - Create new migration"
        echo ""
        echo "Code Quality:"
        echo "  ./dev.sh lint          - Run code linting"
        echo "  ./dev.sh format        - Format code with black"
        echo "  ./dev.sh clean         - Clean cache files"
        echo ""
        echo "Monitoring:"
        echo "  ./dev.sh status        - Check system status"
        echo "  ./dev.sh logs          - Show application logs"
        echo "  ./dev.sh help          - Show this help"
        echo ""
        echo "Quick Start:"
        echo "  1. ./dev.sh setup"
        echo "  2. Edit .env file with your database settings"
        echo "  3. ./dev.sh init-db"
        echo "  4. ./dev.sh dev"
        ;;
esac
