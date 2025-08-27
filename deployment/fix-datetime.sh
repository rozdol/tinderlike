#!/bin/bash

# Fix DateTime Issue Script
# Run this on your EC2 instance to fix the timezone comparison error

set -e

echo "🔧 Fixing datetime timezone issue..."

# Navigate to project directory
cd /var/www/tinderlike

# Stop the current backend
echo "🛑 Stopping current backend..."
pm2 stop tinderlike-backend || echo "Backend was not running"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Test if the fix works
echo "🧪 Testing the fix..."
./venv/bin/python3 -c "
from app.api.offers import calculate_time_until_expiry
from datetime import datetime, timezone
print('✅ DateTime fix test passed')
" || echo "❌ DateTime fix test failed"

# Start the backend again
echo "🚀 Starting backend with fix..."
pm2 start deployment/ecosystem.config.js --env production
pm2 save

# Wait a moment
sleep 3

# Test if backend is responding
echo "🧪 Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is working!"
    echo "🧪 Testing offers endpoint..."
    if curl -s http://localhost:8000/api/v1/offers/next > /dev/null; then
        echo "✅ Offers endpoint is working!"
    else
        echo "❌ Offers endpoint still has issues. Check logs:"
        pm2 logs tinderlike-backend --lines 10 --nostream
    fi
    
    echo "🧪 Testing admin offers endpoint..."
    if curl -s http://localhost:8000/api/v1/admin/offers > /dev/null; then
        echo "✅ Admin offers endpoint is working!"
    else
        echo "❌ Admin offers endpoint still has issues. Check logs:"
        pm2 logs tinderlike-backend --lines 10 --nostream
    fi
else
    echo "❌ Backend is not responding. Check logs:"
    pm2 logs tinderlike-backend --lines 10 --nostream
fi

echo "📋 Next steps:"
echo "1. Check PM2 status: pm2 status"
echo "2. Check logs: pm2 logs tinderlike-backend"
echo "3. Test API: curl http://localhost:8000/api/v1/offers/next"
