#!/bin/bash

# EC2 Instance Setup Script for Tinder-like App
# Run this on your EC2 instance after connecting via SSH

echo "🚀 Setting up EC2 instance for Tinder-like app deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y nginx git curl wget unzip

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

echo "✅ EC2 instance setup complete!"
echo "📋 Next steps:"
echo "1. Clone your repository to /var/www/tinderlike"
echo "2. Set up environment variables"
echo "3. Install Python dependencies"
echo "4. Configure Nginx"
echo "5. Set up SSL certificate"
