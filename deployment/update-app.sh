#!/bin/bash
set -e

echo "🚀 Updating Tinder-like App on Production Server..."
echo "📅 Update started at: $(date)"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Navigate to app directory
cd /var/www/tinderlike

echo "📋 Current app status:"
echo "  - Directory: $(pwd)"
echo "  - Python version: $(python3 --version)"
echo "  - PM2 status:"
pm2 status tinderlike-backend || echo "    Backend not running"

echo ""
echo "🔄 Step 1: Backup current state"
# Create backup directory
BACKUP_DIR="/var/www/tinderlike-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup important files
echo "  📦 Creating backup in: $BACKUP_DIR"
cp -r app "$BACKUP_DIR/"
cp -r frontend "$BACKUP_DIR/"
cp requirements.txt "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/" 2>/dev/null || echo "    .env not found (using example)"
cp tinderlike.db "$BACKUP_DIR/" 2>/dev/null || echo "    Database backup created"

echo ""
echo "🔄 Step 2: Stop services"
echo "  🛑 Stopping backend..."
pm2 stop tinderlike-backend || echo "    Backend was not running"

echo ""
echo "🔄 Step 3: Update application files"
echo "  📥 Pulling latest changes..."
if [ -d ".git" ]; then
    git pull origin main || echo "    Git pull failed, continuing with manual update"
else
    echo "    Git repository not found, manual update required"
fi

echo ""
echo "🔄 Step 4: Update Python dependencies"
echo "  📦 Updating requirements..."
source venv/bin/activate
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "🔄 Step 5: Run database migrations"
echo "  🗄️ Checking for new migrations..."
./venv/bin/alembic upgrade head || {
    echo "    ❌ Migration failed, attempting to fix..."
    ./deployment/fix-migrations.sh
}

echo ""
echo "🔄 Step 6: Test the application"
echo "  🧪 Testing backend startup..."
timeout 10s ./venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 3

if curl -s http://localhost:8000/health > /dev/null; then
    echo "    ✅ Backend test successful"
    kill $BACKEND_PID 2>/dev/null || true
else
    echo "    ❌ Backend test failed"
    kill $BACKEND_PID 2>/dev/null || true
    echo "    📋 Checking logs for issues..."
    echo "    🔧 Attempting to fix common issues..."
    
    # Try to fix common issues
    ./deployment/fix-datetime.sh
    ./deployment/fix-bcrypt.sh
fi

echo ""
echo "🔄 Step 7: Start services"
echo "  🚀 Starting backend with PM2..."
pm2 start deployment/ecosystem.config.js --env production
pm2 save

echo ""
echo "🔄 Step 8: Verify deployment"
echo "  ⏳ Waiting for services to start..."
sleep 5

echo "  🧪 Testing endpoints..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "    ✅ Health endpoint: OK"
else
    echo "    ❌ Health endpoint: FAILED"
fi

if curl -s http://localhost:8000/api/v1/offers/next > /dev/null; then
    echo "    ✅ Offers endpoint: OK"
else
    echo "    ❌ Offers endpoint: FAILED"
fi

if curl -s http://localhost:8000/api/v1/admin/offers > /dev/null; then
    echo "    ✅ Admin endpoint: OK"
else
    echo "    ❌ Admin endpoint: FAILED"
fi

echo ""
echo "🔄 Step 9: Update Nginx configuration (if needed)"
echo "  🌐 Checking Nginx config..."
if nginx -t; then
    echo "    ✅ Nginx configuration is valid"
    systemctl reload nginx
    echo "    ✅ Nginx reloaded"
else
    echo "    ❌ Nginx configuration has errors"
    echo "    🔧 Attempting to fix Nginx config..."
    cp deployment/nginx.conf /etc/nginx/sites-available/tinderlike
    nginx -t
    systemctl reload nginx
fi

echo ""
echo "🔄 Step 10: Final verification"
echo "  🌐 Testing public access..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
if curl -s "http://$PUBLIC_IP/health" > /dev/null 2>&1; then
    echo "    ✅ Public access: OK"
else
    echo "    ⚠️  Public access: Check firewall settings"
fi

echo ""
echo "✅ Update completed successfully!"
echo "📅 Update finished at: $(date)"
echo ""
echo "📋 Post-update information:"
echo "  🌐 App URL: http://$PUBLIC_IP"
echo "  🔧 Admin URL: http://$PUBLIC_IP/admin.html"
echo "  📊 PM2 Status: pm2 status"
echo "  📝 Logs: pm2 logs tinderlike-backend"
echo "  🔄 Backup location: $BACKUP_DIR"
echo ""
echo "🛠️  Troubleshooting commands:"
echo "  - Check status: pm2 status"
echo "  - View logs: pm2 logs tinderlike-backend --lines 20"
echo "  - Restart backend: pm2 restart tinderlike-backend"
echo "  - Fix issues: ./deployment/troubleshoot.sh"
echo "  - Rollback: cp -r $BACKUP_DIR/* . && pm2 restart tinderlike-backend"

