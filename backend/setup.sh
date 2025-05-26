#!/bin/bash

# rwanly Core ERP Backend Setup Script

set -e

echo "🚀 rwanly Core ERP Backend Setup"
echo "================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python 3
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check pip
if ! command_exists pip; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Check PostgreSQL
if ! command_exists psql; then
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed and running."
fi

echo "✅ Prerequisites check completed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
else
    echo "✅ Environment file already exists"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database settings"
echo "2. Make sure PostgreSQL is running"
echo "3. Run: python init_db.py (to initialize database)"
echo "4. Run: uvicorn main:app --reload (to start the server)"
echo ""
echo "API Documentation will be available at:"
echo "- http://localhost:8000/docs (Swagger UI)"
echo "- http://localhost:8000/redoc (ReDoc)"
