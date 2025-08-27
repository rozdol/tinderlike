#!/bin/bash

# Deployment Script for Tinder-like App on EC2
# Run this on your EC2 instance after initial setup

set -e  # Exit on any error

echo "🚀 Deploying Tinder-like app to EC2..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root directory."
    echo "📁 Current directory: $(pwd)"
    echo "📋 Expected files: requirements.txt, app/, frontend/, etc."
    exit 1
fi

# Check if we're running as root (should not be)
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Check and install system dependencies if needed
echo "🔍 Checking system dependencies..."

# Check Python 3.11 (or compatible version)
if ! command -v python3.11 &> /dev/null; then
    echo "🐍 Installing Python 3.11 (or compatible version)..."
    sudo apt-get update
    
    # Check Ubuntu version and install Python accordingly
    UBUNTU_VERSION=$(lsb_release -rs)
    echo "📋 Ubuntu version: $UBUNTU_VERSION"
    
    if [[ "$UBUNTU_VERSION" == "24.04" ]]; then
        echo "📦 Ubuntu 24.04 detected - installing Python 3.12 (latest available)"
        sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip
        # Create symlink for compatibility
        sudo ln -sf /usr/bin/python3.12 /usr/bin/python3.11
        sudo ln -sf /usr/bin/python3.12-venv /usr/bin/python3.11-venv
    elif [[ "$UBUNTU_VERSION" == "22.04" ]]; then
        echo "📦 Ubuntu 22.04 detected - installing Python 3.11"
        sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
    elif [[ "$UBUNTU_VERSION" == "20.04" ]]; then
        echo "📦 Ubuntu 20.04 detected - installing Python 3.11 from deadsnakes PPA"
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt-get update
        sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
    else
        echo "📦 Installing default Python 3"
        sudo apt-get install -y python3 python3-venv python3-dev python3-pip
        # Create symlink for compatibility
        sudo ln -sf /usr/bin/python3 /usr/bin/python3.11
        sudo ln -sf /usr/bin/python3-venv /usr/bin/python3.11-venv
    fi
fi

# Check Nginx
if ! command -v nginx &> /dev/null; then
    echo "🌐 Installing Nginx..."
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Check Node.js and PM2
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if ! command -v pm2 &> /dev/null; then
    echo "⚡ Installing PM2..."
    sudo npm install -g pm2
fi

# Create log directory
echo "📁 Creating log directory..."
sudo mkdir -p /var/log/tinderlike
sudo chown $USER:$USER /var/log/tinderlike

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists, if not create from example
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "⚠️  Please edit .env file with your production settings before continuing."
        echo "   Press Enter when ready to continue..."
        read
    else
        echo "❌ Error: No .env file found and no env.example available."
        echo "   Please create a .env file with your production settings."
        exit 1
    fi
fi

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Seed database with initial data
echo "🌱 Seeding database..."
python scripts/seed_data.py

# Set up Nginx configuration
echo "🌐 Setting up Nginx..."

# Check if deployment directory exists
if [ ! -d "deployment" ]; then
    echo "❌ Error: deployment directory not found."
    echo "   Please make sure you're running this from the project root."
    exit 1
fi

# Copy Nginx configuration
if [ -f "deployment/nginx.conf" ]; then
    sudo cp deployment/nginx.conf /etc/nginx/sites-available/tinderlike
    
    # Update the server_name in nginx.conf with actual IP
    ACTUAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
    sudo sed -i "s/your-ec2-public-ip-or-domain.com/$ACTUAL_IP/g" /etc/nginx/sites-available/tinderlike
    
    sudo ln -sf /etc/nginx/sites-available/tinderlike /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site
else
    echo "❌ Error: deployment/nginx.conf not found."
    exit 1
fi

# Test Nginx configuration
echo "🔍 Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Start the application with PM2
echo "⚡ Starting application with PM2..."

# Check if ecosystem.config.js exists
if [ -f "deployment/ecosystem.config.js" ]; then
    # Update the host in ecosystem.config.js with actual IP
    ACTUAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
    sed -i "s/your-ec2-public-ip/$ACTUAL_IP/g" deployment/ecosystem.config.js
    
    pm2 start deployment/ecosystem.config.js --env production
    pm2 save
    pm2 startup
else
    echo "❌ Error: deployment/ecosystem.config.js not found."
    exit 1
fi

# Set up firewall (if using UFW)
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Get the actual public IP
ACTUAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "your-ec2-public-ip")

echo "✅ Deployment complete!"
echo "🌐 Your app should be accessible at: http://$ACTUAL_IP"
echo "📋 Useful commands:"
echo "  - View logs: pm2 logs tinderlike-backend"
echo "  - Restart app: pm2 restart tinderlike-backend"
echo "  - Stop app: pm2 stop tinderlike-backend"
echo "  - Monitor: pm2 monit"
echo "  - Check status: pm2 status"
echo "  - View Nginx logs: sudo tail -f /var/log/nginx/error.log"
