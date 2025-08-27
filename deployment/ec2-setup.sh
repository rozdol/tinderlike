#!/bin/bash

# EC2 Instance Setup Script for Tinder-like App
# Run this on your EC2 instance after connecting via SSH

set -e  # Exit on any error

echo "🚀 Setting up EC2 instance for Tinder-like app deployment..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
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

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y nginx git curl wget unzip sqlite3

# Install Node.js (for potential frontend build tools)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/tinderlike
sudo chown $USER:$USER /var/www/tinderlike

# Install PM2 for process management
echo "⚡ Installing PM2..."
sudo npm install -g pm2

# Set up basic firewall
echo "🔥 Setting up basic firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

echo "✅ EC2 instance setup complete!"
echo "📋 Next steps:"
echo "1. Clone your repository: git clone <your-repo> /var/www/tinderlike"
echo "2. Navigate to project: cd /var/www/tinderlike"
echo "3. Run deployment: ./deployment/deploy.sh"
echo ""
echo "🌐 Your instance is ready for deployment!"
