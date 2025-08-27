#!/bin/bash
set -e
echo "🔧 Fixing bcrypt compatibility issue..."
cd /var/www/tinderlike

echo "🛑 Stopping backend..."
pm2 stop tinderlike-backend || echo "Backend was not running"

echo "📦 Updating bcrypt to compatible version..."
source venv/bin/activate
./venv/bin/pip uninstall -y bcrypt || echo "bcrypt not installed"
./venv/bin/pip install bcrypt==4.0.1

echo "🧪 Testing bcrypt fix..."
./venv/bin/python3 -c "
from passlib.hash import bcrypt
print('✅ bcrypt compatibility test passed')
" || echo "❌ bcrypt compatibility test failed"

echo "🚀 Starting backend..."
pm2 start deployment/ecosystem.config.js --env production
pm2 save

sleep 3
echo "🧪 Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is working!"
    echo "✅ bcrypt error should be resolved!"
else
    echo "❌ Backend is not responding. Check logs:"
    pm2 logs tinderlike-backend --lines 10 --nostream
fi

echo "📋 Next steps:"
echo "1. Check PM2 status: pm2 status"
echo "2. Check logs: pm2 logs tinderlike-backend"
echo "3. The bcrypt error should no longer appear in logs"
