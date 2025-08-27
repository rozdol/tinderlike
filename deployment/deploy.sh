#!/bin/bash

# Deployment Script for Tinder-like App on EC2
# Run this on your EC2 instance after initial setup

echo "🚀 Deploying Tinder-like app to EC2..."

# Navigate to application directory
cd /var/www/tinderlike

# Create log directory
sudo mkdir -p /var/log/tinderlike
sudo chown $USER:$USER /var/log/tinderlike

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Seed database with initial data
echo "🌱 Seeding database..."
python scripts/seed_data.py

# Set up Nginx configuration
echo "🌐 Setting up Nginx..."
sudo cp deployment/nginx.conf /etc/nginx/sites-available/tinderlike
sudo ln -sf /etc/nginx/sites-available/tinderlike /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

# Start the application with PM2
echo "⚡ Starting application with PM2..."
pm2 start deployment/ecosystem.config.js --env production
pm2 save
pm2 startup

# Set up firewall (if using UFW)
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

echo "✅ Deployment complete!"
echo "🌐 Your app should be accessible at: http://your-ec2-public-ip"
echo "📋 Useful commands:"
echo "  - View logs: pm2 logs tinderlike-backend"
echo "  - Restart app: pm2 restart tinderlike-backend"
echo "  - Stop app: pm2 stop tinderlike-backend"
echo "  - Monitor: pm2 monit"
