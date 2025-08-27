#!/bin/bash

# TinderLike Offers - Simple Start Script

echo "🚀 Starting TinderLike Offers Application (Simple Version)..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies (simple version)
echo "📥 Installing dependencies (simple version)..."
pip install -r requirements-simple.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   You can use any text editor to modify the .env file."
    read -p "Press Enter when you've configured .env file..."
fi

# Update config to use simple config
echo "🗄️  Configuring simple database..."
cp app/config-simple.py app/config.py

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Seed database with sample data
echo "🌱 Seeding database with sample data..."
python scripts/seed_data.py

# Start the application
echo "🎯 Starting FastAPI application..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "📚 API documentation will be available at: http://localhost:8000/docs"
echo "🏥 Health check will be available at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the FastAPI server
python run.py
