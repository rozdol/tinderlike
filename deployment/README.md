# 🚀 EC2 Deployment Guide for Tinder-like App

This guide will help you deploy your Tinder-like app to an AWS EC2 instance so it's accessible via the internet.

## 📋 Prerequisites

1. **AWS EC2 Instance** running Ubuntu 20.04 or later
2. **Domain Name** (optional but recommended for SSL)
3. **GitHub Repository** with your code
4. **SSH Access** to your EC2 instance

## 🚀 Quick Start (3 Steps)

1. **Setup EC2**: Run `ec2-setup.sh` to install dependencies
2. **Clone & Deploy**: Clone your repo and run `deploy.sh`
3. **Access App**: Visit `http://your-ec2-ip`

**Complete commands:**
```bash
# Step 1: Setup EC2
curl -sSL https://raw.githubusercontent.com/rozdol/tinderlike/refs/heads/main/deployment/ec2-setup.sh | bash

# Step 2: Clone and deploy
cd /var/www
git clone https://github.com/rozdol/tinderlike.git tinderlike
cd tinderlike
cp deployment/production.env .env
nano .env  # Edit with your settings
chmod +x deployment/*.sh
./deployment/deploy.sh

# Step 3: Access your app
# Visit: http://your-ec2-public-ip
```

**📋 Supported Ubuntu Versions:**
- Ubuntu 24.04 (Noble): Uses Python 3.12
- Ubuntu 22.04 (Jammy): Uses Python 3.11
- Ubuntu 20.04 (Focal): Uses Python 3.11 (from PPA)
- Other versions: Uses default Python 3

## 🔧 Step 1: EC2 Instance Setup

### 1.1 Connect to your EC2 instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 1.2 Run the setup script
```bash
# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/rozdol/tinderlike/refs/heads/main/deployment/ec2-setup.sh | bash
```

**⚠️ Important**: This script only sets up the EC2 instance with required dependencies. 
It does NOT deploy your application yet. You need to complete Step 2 to deploy your app.

**OR** manually run these commands:
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install Nginx and other dependencies
sudo apt-get install -y nginx git curl wget unzip sqlite3

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Create application directory
sudo mkdir -p /var/www/tinderlike
sudo chown $USER:$USER /var/www/tinderlike

# Set up basic firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
```

## 📦 Step 2: Deploy Your Application

### 2.1 Clone your repository
```bash
cd /var/www
git clone https://github.com/your-username/your-repo.git tinderlike
cd tinderlike
```

### 2.2 Set up environment variables
```bash
# Copy the production environment file
cp deployment/production.env .env

# Edit the environment file with your settings
nano .env
```

**Important**: Update these values in `.env`:
- `SECRET_KEY`: Generate a strong secret key (use: `openssl rand -hex 32`)
- `FRONTEND_URL`: Your EC2 public IP or domain
- Email/SMS settings if you want notifications

### 2.3 Run the deployment script
```bash
# Make scripts executable
chmod +x deployment/*.sh

# Run the deployment script
./deployment/deploy.sh
```

**Note**: The deployment script will:
- Check and install missing dependencies
- Create virtual environment
- Install Python packages
- Set up database
- Configure Nginx
- Start the application with PM2

## 🌐 Step 3: Configure Domain and SSL (Optional but Recommended)

### 3.1 Point your domain to EC2
Add an A record in your DNS settings:
```
Type: A
Name: @
Value: your-ec2-public-ip
```

### 3.2 Set up SSL certificate
```bash
chmod +x deployment/ssl-setup.sh
./deployment/ssl-setup.sh
```

## 🔍 Step 4: Verify Deployment

### 4.1 Check if services are running
```bash
# Check PM2 processes
pm2 status

# Check Nginx status
sudo systemctl status nginx

# Check application logs
pm2 logs tinderlike-backend
```

### 4.2 Test your application
- **Frontend**: `http://your-ec2-public-ip` or `https://your-domain.com`
- **Backend API**: `http://your-ec2-public-ip/api/` or `https://your-domain.com/api/`
- **Health Check**: `http://your-ec2-public-ip/health` or `https://your-domain.com/health`
- **Admin Panel**: `http://your-ec2-public-ip/admin` or `https://your-domain.com/admin`

## 🛠️ Step 5: Useful Commands

### Application Management
```bash
# View application logs
pm2 logs tinderlike-backend

# Restart application
pm2 restart tinderlike-backend

# Stop application
pm2 stop tinderlike-backend

# Monitor application
pm2 monit

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Management
```bash
# Access SQLite database
sqlite3 tinderlike.db

# Run database migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py
```

### Security
```bash
# Update firewall rules
sudo ufw status
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS

# Update system packages
sudo apt-get update && sudo apt-get upgrade -y
```

## 🔧 Step 6: Troubleshooting

### Common Issues

#### 1. Application not starting
```bash
# Check PM2 logs
pm2 logs tinderlike-backend

# Check if port 8000 is in use
sudo netstat -tlnp | grep :8000

# Restart PM2
pm2 restart all
```

#### 2. Nginx not serving files
```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

#### 3. Database issues
```bash
# Check database file permissions
ls -la tinderlike.db

# Recreate database
rm tinderlike.db
alembic upgrade head
python scripts/seed_data.py

# If migrations fail, use the fix script
chmod +x deployment/fix-migrations.sh
./deployment/fix-migrations.sh
python scripts/seed_data.py
```

#### 4. SSL certificate issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check SSL configuration
sudo nginx -t
```

## 📊 Step 7: Monitoring and Maintenance

### Set up monitoring
```bash
# Install monitoring tools
sudo apt-get install -y htop iotop

# Monitor system resources
htop
```

### Regular maintenance
```bash
# Update system packages (weekly)
sudo apt-get update && sudo apt-get upgrade -y

# Renew SSL certificate (automatic, but check monthly)
sudo certbot renew --dry-run

# Clean up logs (monthly)
sudo journalctl --vacuum-time=30d
```

## 🔐 Security Best Practices

1. **Change default SSH port** (optional)
2. **Use SSH keys only** (disable password authentication)
3. **Keep system updated**
4. **Use strong passwords** for admin accounts
5. **Enable firewall** (UFW)
6. **Use HTTPS** with SSL certificates
7. **Regular backups** of database and configuration files

## 📞 Support

If you encounter issues:
1. Check the logs: `pm2 logs tinderlike-backend`
2. Verify configuration files
3. Test individual components
4. Check AWS EC2 console for instance status

Your app should now be accessible via the internet! 🎉
