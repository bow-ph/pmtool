# DocuPlanAI Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- Redis
- Nginx

## Quick Start Guide

### 1. Environment Variables

#### Required API Keys
```bash
# OpenAI API Key for PDF Analysis
OPENAI_API_KEY=__OPENAI_API_KEY__

# Mollie Payment Integration
MOLLIE_TEST_API_KEY=__MOLLIE_TEST_API_KEY__
MOLLIE_LIVE_API_KEY=__MOLLIE_LIVE_API_KEY__

# SendGrid Email Service
SENDGRID_API_KEY=__SENDGRID_API_KEY__
```

#### Database Configuration
```bash
# PostgreSQL Settings
DB_NAME=pmtool
DB_USER=pmtool
DB_PASSWORD=__DB_PASSWORD__
DB_HOST=__DB_HOST__

# Redis Configuration
REDIS_URL=redis://__REDIS_HOST__:6379
REDIS_PASSWORD=__REDIS_PASSWORD__

# CalDAV Configuration
CALDAV_URL=http://__CALDAV_HOST__:5232
CALDAV_PUBLIC_URL=https://docuplanai.com/caldav
```

#### Security Configuration
```bash
# JWT and Session Security
JWT_SECRET=__JWT_SECRET__
SESSION_SECRET=__SESSION_SECRET__

# Service Configuration
DEBUG=False
ALLOWED_HOSTS=admin.docuplanai.com,localhost
CORS_ORIGINS=https://docuplanai.com,http://localhost:3000
```

Note: Never commit `.env` files to version control. Use `config.template.env` as a template and run `prepare_env.sh` to generate secure credentials.

### 2. Service Configuration

#### Configure System User
```bash
# Ensure www-data user exists and has correct permissions
sudo usermod -d /var/www www-data
sudo chown -R www-data:www-data /var/www
```

#### Setup Services
```bash
# Run setup script with www-data user
sudo -u www-data ./deploy/setup_services.sh

# Verify service permissions
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status radicale
```

### 3. Deploy Application

#### Prepare Environment
```bash
# Copy environment templates
cp deploy/config.template.env backend/.env
cp deploy/config.template.env frontend/.env.production

# Run environment preparation script
./deploy/prepare_env.sh
```

#### Deploy Services
```bash
# Deploy backend and frontend
./deploy/deploy_beta.sh

# Verify deployment
sudo -u www-data systemctl status docuplanai-backend
sudo systemctl status nginx
```

## Service Verification

### Backend Services
```bash
# Check backend service status
systemctl status docuplanai-backend

# Check logs
journalctl -u docuplanai-backend -f
```

### Frontend Services
```bash
# Check nginx configuration
nginx -t

# Check nginx status
systemctl status nginx
```

## Troubleshooting

### Common Issues

1. **Permission Issues**
   - Verify www-data ownership: `sudo ls -l /var/www/docuplanai`
   - Check service permissions: `sudo -u www-data systemctl status docuplanai-backend`
   - Fix permissions if needed: `sudo chown -R www-data:www-data /var/www/docuplanai`

2. **Database Connection**
   - Check PostgreSQL status: `sudo systemctl status postgresql`
   - Verify database credentials in `.env`
   - Test database connection: `sudo -u www-data psql -U pmtool -d pmtool -h localhost`

3. **Redis Connection**
   - Check Redis status: `sudo systemctl status redis-server`
   - Verify Redis password in `.env`
   - Test Redis connection: `redis-cli ping`

4. **Email Service**
   - Verify SendGrid API key in `.env`
   - Check email logs: `sudo journalctl -u docuplanai-backend | grep "email"`
   - Test email service: `curl -X POST https://admin.docuplanai.com/v1/test-email`

5. **CalDAV Synchronization**
   - Check Radicale service: `sudo systemctl status radicale`
   - Verify CalDAV endpoints in `.env`
   - Test CalDAV access: `curl -u user:pass https://docuplanai.com/caldav`

For detailed deployment instructions, see `DEPLOYMENT.md`.
