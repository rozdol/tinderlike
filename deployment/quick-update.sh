#!/bin/bash
# Quick update script - run this on your EC2 instance
set -e

echo "🚀 Quick Update - Tinder-like App"
echo "📅 Started at: $(date)"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Run with: sudo bash deployment/quick-update.sh"
    exit 1
fi

cd /var/www/tinderlike

# Stop backend
echo "🛑 Stopping backend..."
pm2 stop tinderlike-backend || echo "Backend was not running"

# Update files (git pull or manual)
echo "📥 Updating files..."
if [ -d ".git" ]; then
    git pull origin main || echo "Git pull failed - check manually"
else
    echo "⚠️  No git repo - update files manually"
fi

# Update dependencies
echo "📦 Updating dependencies..."
source venv/bin/activate
./venv/bin/pip install -r requirements.txt

# Run migrations
echo "🗄️ Running migrations..."
./venv/bin/alembic upgrade head || echo "Migration failed - check logs"

# Start backend
echo "🚀 Starting backend..."
pm2 start deployment/ecosystem.config.js --env production
pm2 save

# Test
echo "🧪 Testing..."
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Update successful!"
    echo "🌐 App should be available at your EC2 IP"
else
    echo "❌ Update failed - check logs: pm2 logs tinderlike-backend"
fi

echo "📅 Finished at: $(date)"

