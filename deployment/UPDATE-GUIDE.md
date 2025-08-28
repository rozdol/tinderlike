# 🚀 Production Update Guide

This guide explains how to safely update the Tinder-like app on your production server.

## 📋 Prerequisites

- **Root access** to the EC2 instance
- **SSH connection** to the server
- **Git repository** with latest changes (or manual file upload)

## 🎯 Quick Update (Recommended)

### Option 1: Automated Update Script

```bash
# SSH to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Switch to root
sudo su

# Navigate to app directory
cd /var/www/tinderlike

# Make update script executable
chmod +x deployment/update-app.sh

# Run the automated update
./deployment/update-app.sh
```

### Option 2: Manual Update Steps

If you prefer manual control or the automated script fails:

```bash
# 1. SSH to server and switch to root
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo su

# 2. Navigate to app directory
cd /var/www/tinderlike

# 3. Create backup
BACKUP_DIR="/var/www/tinderlike-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r app frontend requirements.txt .env tinderlike.db "$BACKUP_DIR/"

# 4. Stop services
pm2 stop tinderlike-backend

# 5. Update files (choose one method)
# Method A: Git pull
git pull origin main

# Method B: Manual file upload
# Upload new files via SCP or SFTP

# 6. Update dependencies
source venv/bin/activate
./venv/bin/pip install -r requirements.txt

# 7. Run migrations
./venv/bin/alembic upgrade head

# 8. Test backend
timeout 10s ./venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3
curl http://localhost:8000/health
kill %1

# 9. Start services
pm2 start deployment/ecosystem.config.js --env production
pm2 save

# 10. Verify deployment
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/offers/next
```

## 🔄 What's New in This Update

### ✨ Advanced Swipe Animations
- **Touch gestures**: Swipe left/right on mobile devices
- **Mouse drag**: Click and drag on desktop
- **Visual feedback**: Real-time card transformation
- **Smooth animations**: Professional-grade transitions
- **Swipe indicators**: "LIKE" and "PASS" visual cues

### 🐛 Bug Fixes
- **DateTime issues**: Fixed timezone comparison errors
- **bcrypt compatibility**: Resolved passlib warnings
- **Admin API**: Fixed admin offers endpoint errors

### 🎨 UI Improvements
- **Button animations**: Press feedback with color-coded pulses
- **Card entrance**: Smooth slide-in for new offers
- **Ripple effects**: Material design button interactions
- **Performance**: Optimized for 60fps animations

## 📁 Files Updated

### Frontend Files
- `frontend/app.js` - Added swipe gesture support
- `frontend/styles.css` - New animations and visual effects
- `frontend/index.html` - Added swipe indicators

### Backend Files
- `app/api/offers.py` - Fixed datetime timezone issues
- `app/api/admin.py` - Fixed admin datetime issues
- `requirements.txt` - Updated bcrypt version

### Deployment Files
- `deployment/update-app.sh` - New automated update script
- `deployment/fix-datetime.sh` - DateTime fix script
- `deployment/fix-bcrypt.sh` - bcrypt compatibility fix

## 🛠️ Troubleshooting

### Common Issues

#### 1. Update Script Fails
```bash
# Check permissions
chmod +x deployment/update-app.sh

# Run with verbose output
bash -x deployment/update-app.sh
```

#### 2. Backend Won't Start
```bash
# Check logs
pm2 logs tinderlike-backend --lines 20

# Try manual fix
./deployment/fix-datetime.sh
./deployment/fix-bcrypt.sh

# Restart backend
pm2 restart tinderlike-backend
```

#### 3. Database Migration Issues
```bash
# Fix migrations
./deployment/fix-migrations.sh

# Or reset database (⚠️ WARNING: Loses data)
rm tinderlike.db
./venv/bin/alembic upgrade head
./venv/bin/python3 scripts/seed_data.py
```

#### 4. Nginx Issues
```bash
# Check Nginx config
nginx -t

# Reload Nginx
systemctl reload nginx

# Check Nginx logs
tail -f /var/log/nginx/error.log
```

### Rollback Procedure

If something goes wrong, you can rollback to the previous version:

```bash
# Find backup directory
ls -la /var/www/tinderlike-backup-*

# Stop services
pm2 stop tinderlike-backend

# Restore from backup
BACKUP_DIR="/var/www/tinderlike-backup-YYYYMMDD-HHMMSS"
cp -r "$BACKUP_DIR"/* .

# Restart services
pm2 start deployment/ecosystem.config.js --env production
pm2 save
```

## 🔍 Verification Checklist

After updating, verify these items:

- [ ] **Health endpoint**: `curl http://localhost:8000/health`
- [ ] **Offers endpoint**: `curl http://localhost:8000/api/v1/offers/next`
- [ ] **Admin endpoint**: `curl http://localhost:8000/api/v1/admin/offers`
- [ ] **Frontend loads**: Visit your app URL in browser
- [ ] **Swipe gestures work**: Try swiping cards on mobile/desktop
- [ ] **Admin panel**: Check admin.html loads correctly
- [ ] **No errors in logs**: `pm2 logs tinderlike-backend --lines 10`

## 📞 Support

If you encounter issues:

1. **Check logs**: `pm2 logs tinderlike-backend`
2. **Run troubleshoot**: `./deployment/troubleshoot.sh`
3. **Check status**: `pm2 status`
4. **Verify config**: Check `.env` file settings

## 🎉 Success Indicators

You'll know the update was successful when:

- ✅ App loads without errors
- ✅ Swipe animations work smoothly
- ✅ No datetime errors in logs
- ✅ No bcrypt warnings
- ✅ Admin panel functions correctly
- ✅ All endpoints return 200 OK

---

**Last Updated**: $(date)
**Version**: 1.1.0
**Compatibility**: Python 3.11+, Ubuntu 20.04/22.04/24.04

