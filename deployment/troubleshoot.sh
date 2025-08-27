#!/bin/bash

# Troubleshooting Script for Tinder-like App
# Run this on your EC2 instance to diagnose issues

set -e

echo "🔍 Troubleshooting Tinder-like App..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this from the project root."
    exit 1
fi

echo "📋 System Information:"
echo "  - Current directory: $(pwd)"
echo "  - User: $(whoami)"
echo "  - Date: $(date)"

# Check if virtual environment exists
echo ""
echo "🐍 Checking Python environment..."
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Check if .env file exists
echo ""
echo "⚙️ Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Creating from example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "⚠️  Please edit .env file with your production settings"
    else
        echo "❌ No env.example found. Please create .env file manually"
    fi
fi

# Check database
echo ""
echo "🗄️ Checking database..."
if [ ! -f "tinderlike.db" ]; then
    echo "❌ Database not found. Creating..."
    alembic upgrade head
    python scripts/seed_data.py
fi

# Check if backend is running
echo ""
echo "🚀 Checking backend status..."
if command -v pm2 &> /dev/null; then
    echo "📊 PM2 Status:"
    pm2 status
    
    echo ""
    echo "📋 PM2 Logs (last 20 lines):"
    pm2 logs tinderlike-backend --lines 20 --nostream || echo "No logs available"
else
    echo "❌ PM2 not found. Installing..."
    sudo npm install -g pm2
fi

# Check if port 8000 is in use
echo ""
echo "🔌 Checking port 8000..."
if netstat -tlnp 2>/dev/null | grep :8000; then
    echo "✅ Port 8000 is in use"
else
    echo "❌ Port 8000 is not in use"
fi

# Check Nginx status
echo ""
echo "🌐 Checking Nginx status..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
    echo "📋 Nginx configuration test:"
    sudo nginx -t
    
    echo ""
    echo "📋 Nginx error logs (last 10 lines):"
    sudo tail -n 10 /var/log/nginx/error.log
else
    echo "❌ Nginx is not running"
    echo "🔄 Starting Nginx..."
    sudo systemctl start nginx
    sudo systemctl enable nginx
fi

# Check firewall
echo ""
echo "🔥 Checking firewall..."
sudo ufw status

# Check if backend can start manually
echo ""
echo "🧪 Testing backend startup..."
cd /var/www/tinderlike
source venv/bin/activate

# Try to start the backend manually
echo "📝 Attempting to start backend manually..."
timeout 10s python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 || echo "Backend startup test completed"

# Restart services
echo ""
echo "🔄 Restarting services..."
if command -v pm2 &> /dev/null; then
    pm2 restart tinderlike-backend || echo "PM2 restart failed"
fi

sudo systemctl restart nginx

echo ""
echo "✅ Troubleshooting complete!"
echo "📋 Next steps:"
echo "1. Check the logs above for errors"
echo "2. If PM2 shows no processes, run: pm2 start deployment/ecosystem.config.js"
echo "3. If Nginx shows errors, check: sudo nginx -t"
echo "4. Test the API: curl http://localhost:8000/health"
