#!/bin/bash

# Quick Fix for Python Command Issue
# Run this on your EC2 instance

set -e

echo "🔧 Quick fix for Python command issue..."

# Navigate to project directory
cd /var/www/tinderlike

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check what Python is available in venv
echo "🐍 Checking Python in virtual environment..."
ls -la venv/bin/python*

# Create symlink if needed
if [ ! -f "venv/bin/python" ] && [ -f "venv/bin/python3" ]; then
    echo "🔗 Creating python symlink..."
    ln -sf venv/bin/python3 venv/bin/python
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if backend can start
echo "🚀 Testing backend startup..."
python3 -c "import uvicorn; print('✅ uvicorn available')" || echo "❌ uvicorn not available"

# Try to start backend
echo "📝 Starting backend..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment
sleep 3

# Test if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is working!"
    echo "🔄 Stopping test backend..."
    kill $BACKEND_PID 2>/dev/null || true
    
    echo "🚀 Starting with PM2..."
    pm2 start deployment/ecosystem.config.js --env production
    pm2 save
    
    echo "✅ Backend should now be running with PM2!"
else
    echo "❌ Backend is not responding. Check the logs above."
    kill $BACKEND_PID 2>/dev/null || true
fi

echo "📋 Next steps:"
echo "1. Check PM2 status: pm2 status"
echo "2. Check logs: pm2 logs tinderlike-backend"
echo "3. Test API: curl http://localhost:8000/health"
