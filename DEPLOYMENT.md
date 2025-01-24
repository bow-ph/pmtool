# DocuPlanAI Deployment Guide

## Prerequisites
- Ubuntu Server 20.04 LTS or higher
- Python 3.12
- Node.js 18+
- PostgreSQL 12+
- Redis
- Nginx

## Environment Variables
Create a `.env` file in both the backend and frontend directories. Use the provided templates and replace the placeholders with actual values.

### Required Environment Variables:
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
MOLLIE_TEST_API_KEY=your_mollie_test_key
MOLLIE_LIVE_API_KEY=your_mollie_live_key
SENDGRID_API_KEY=your_sendgrid_api_key

# Database Configuration
DB_NAME=pmtool
DB_USER=pmtool
DB_PASSWORD=your_secure_password
DB_HOST=localhost

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# CalDAV Configuration
CALDAV_URL=http://localhost:5232
CALDAV_PUBLIC_URL=https://docuplanai.com/caldav

# Application URLs
FRONTEND_URL=https://docuplanai.com
BACKEND_URL=https://admin.docuplanai.com

# Email Configuration
EMAILS_FROM_EMAIL=noreply@docuplanai.com
EMAILS_FROM_NAME=DocuPlanAI
```

## Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/bow-ph/pmtool.git
cd pmtool
```

### 2. Setup Services
```bash
# Run the service setup script
chmod +x deploy/setup_services.sh
sudo ./deploy/setup_services.sh
```

### 3. Configure Environment
```bash
# Copy and edit environment files
cp deploy/config.template.env backend/.env
cp deploy/config.template.env frontend/.env.production

# Update environment variables
./deploy/prepare_env.sh
```

### 4. Deploy Backend
```bash
# Deploy backend services
chmod +x deploy/backend.sh
./deploy/backend.sh
```

### 5. Deploy Frontend
```bash
# Deploy frontend application
chmod +x deploy/frontend.sh
./deploy/frontend.sh
```

### 6. Configure Nginx
The deployment scripts will automatically configure Nginx for both frontend and backend services. The configurations will be created at:
- `/etc/nginx/sites-available/docuplanai.conf`
- `/etc/nginx/sites-available/admin.docuplanai.conf`

### 7. SSL Configuration (Optional but Recommended)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificates
sudo certbot --nginx -d docuplanai.com -d admin.docuplanai.com
```

## Post-Deployment Verification

### 1. Check Services
```bash
# Verify service status
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status radicale
sudo systemctl status docuplanai-backend
sudo systemctl status nginx
```

### 2. Test Endpoints
```bash
# Test backend API
curl https://admin.docuplanai.com/v1/health

# Test frontend
curl https://docuplanai.com
```

### 3. Monitor Logs
```bash
# Backend logs
sudo journalctl -u docuplanai-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env`
   - Verify database migrations: `alembic upgrade head`

2. **Redis Connection Issues**
   - Verify Redis is running: `sudo systemctl status redis-server`
   - Check Redis configuration in `/etc/redis/redis.conf`
   - Test Redis connection: `redis-cli ping`

3. **CalDAV Synchronization Issues**
   - Verify Radicale is running: `sudo systemctl status radicale`
   - Check Radicale logs: `sudo journalctl -u radicale -f`
   - Verify CalDAV endpoints in `.env`

4. **Email Sending Issues**
   - Verify SendGrid API key
   - Check email service logs
   - Test email configuration

## Security Considerations

1. **Environment Variables**
   - Keep `.env` files secure and restrict access
   - Regularly rotate API keys and passwords
   - Use strong passwords for all services

2. **File Permissions**
   - Ensure proper ownership: `sudo chown -R www-data:www-data /var/www/docuplanai`
   - Set correct permissions: `sudo chmod -R 750 /var/www/docuplanai`

3. **Firewall Configuration**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Backup and Maintenance

### Database Backup
```bash
# Create backup script
cat > /etc/cron.daily/backup-pmtool << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/pmtool"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
pg_dump pmtool > $BACKUP_DIR/pmtool_$DATE.sql
find $BACKUP_DIR -type f -mtime +7 -delete
EOF

# Make backup script executable
chmod +x /etc/cron.daily/backup-pmtool
```

### Log Rotation
```bash
# Configure log rotation
cat > /etc/logrotate.d/docuplanai << 'EOF'
/var/log/docuplanai/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 640 www-data adm
}
EOF
```

## Monitoring

### Setup Basic Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop netdata

# Configure netdata
sudo systemctl enable netdata
sudo systemctl start netdata
```

Access monitoring dashboard at `http://your-server-ip:19999`

## Support and Documentation
For additional support or questions, please refer to:
- GitHub Repository: https://github.com/bow-ph/pmtool
- Documentation: https://docuplanai.com/docs
- Support Email: support@docuplanai.com
