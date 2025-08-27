#!/bin/bash

# Fix 502 Bad Gateway Error Script
# Run this on your EC2 instance to fix common 502 errors

set -e

echo "🔧 Fixing 502 Bad Gateway Error..."

# Navigate to project directory
cd /var/www/tinderlike

# Check if backend is running
echo "🚀 Checking backend status..."
if ! pm2 list | grep -q "tinderlike-backend"; then
    echo "❌ Backend not running. Starting it..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start backend with PM2
    pm2 start deployment/ecosystem.config.js --env production
    pm2 save
    pm2 startup
else
    echo "✅ Backend is running. Restarting it..."
    pm2 restart tinderlike-backend
fi

# Check if port 8000 is accessible
echo "🔌 Testing backend connectivity..."
sleep 3

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is responding on port 8000"
else
    echo "❌ Backend is not responding. Checking logs..."
    pm2 logs tinderlike-backend --lines 10 --nostream
    
    echo "🔄 Attempting to restart backend..."
    pm2 stop tinderlike-backend
    sleep 2
    pm2 start tinderlike-backend
fi

# Check Nginx configuration
echo "🌐 Checking Nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    sudo systemctl restart nginx
else
    echo "❌ Nginx configuration has errors. Fixing..."
    
    # Backup current config
    sudo cp /etc/nginx/sites-available/tinderlike /etc/nginx/sites-available/tinderlike.backup
    
    # Update with correct configuration
    sudo tee /etc/nginx/sites-available/tinderlike << 'EOF'
server {
    listen 80;
    server_name _;  # Accept any hostname

    # Frontend static files
    location / {
        root /var/www/tinderlike/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin panel
    location /admin {
        root /var/www/tinderlike/frontend;
        try_files $uri $uri/ /admin.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
}
EOF

    # Test and restart Nginx
    sudo nginx -t
    sudo systemctl restart nginx
fi

# Check firewall
echo "🔥 Checking firewall..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Final test
echo "🧪 Testing the fix..."
sleep 2

if curl -s http://localhost/health > /dev/null; then
    echo "✅ Fix successful! App should be accessible now."
    echo "🌐 Try accessing: http://your-ec2-public-ip"
else
    echo "❌ Still having issues. Running full troubleshooting..."
    ./deployment/troubleshoot.sh
fi
