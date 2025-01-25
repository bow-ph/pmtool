# DocuPlanAI Setup Guide

## Default Access Credentials

### Frontend (https://docuplanai.com)
```bash
# Admin User
Email: admin@docuplanai.com
Password: [Generated during deployment]

# Test User
Email: test@docuplanai.com
Password: [Generated during deployment]
```

### Backend Admin UI (https://admin.docuplanai.com)
```bash
# Admin User
Email: admin@docuplanai.com
Password: [Generated during deployment]

# Database Access
User: pmtool
Password: [Generated during deployment]
Database: pmtool
Host: localhost

# Redis Access
Host: localhost
Port: 6379
Password: [Generated during deployment]
SSL: false

# CalDAV Access
User: caldav
Password: [Generated during deployment]
URL: https://docuplanai.com/caldav
Host: localhost
Port: 5232
SSL: false

# API Keys
OpenAI API: [Managed through secrets]
Mollie Test: [Managed through secrets]
Mollie Live: [Managed through secrets]
SendGrid: [Managed through secrets]
```

Note: All credentials are automatically generated during deployment for security. Initial passwords will be displayed in the deployment output. Change all passwords immediately after first login. API keys are managed through the secrets system and should never be committed to version control.

## Quick Start Guide

### 1. Environment Variables and Credentials

The following environment variables are required for deployment. All sensitive values will be automatically generated or pulled from secrets during deployment.

#### API Keys and External Services
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
DATABASE_NAME=pmtool
DATABASE_USER=pmtool
DATABASE_PASSWORD=__DB_PASSWORD__  # Generated during deployment
DATABASE_HOST=__DB_HOST__

# Redis Configuration
REDIS_HOST=__REDIS_HOST__
REDIS_PORT=6379
REDIS_PASSWORD=__REDIS_PASSWORD__  # Generated during deployment
REDIS_SSL=false

# CalDAV Configuration
CALDAV_HOST=__CALDAV_HOST__
CALDAV_PORT=5232
CALDAV_SSL=false
CALDAV_PUBLIC_URL=https://docuplanai.com/caldav
```

#### Security Configuration
```bash
# JWT and Session Security (Generated during deployment)
JWT_SECRET=__JWT_SECRET__
SESSION_SECRET=__SESSION_SECRET__

# Server Configuration
SERVER_IP=__SERVER_IP_DOCUPLANAI__
SERVER_PASSWORD=__SERVER_PASSWORD_DOCUPLANAI__

# Service Configuration
DEBUG=false
ALLOWED_HOSTS='["admin.docuplanai.com", "localhost"]'
CORS_ORIGINS='["https://docuplanai.com", "http://localhost:3000"]'
```

Note: All placeholders with `__VARIABLE__` format will be automatically replaced during deployment by the `prepare_env.sh` script. Never commit actual credentials to the repository.

### Access Credentials

#### Frontend UI (docuplanai.com)
```
Admin User:
Email: admin@docuplanai.com
Password: [Generated during deployment]

Test User:
Email: test@docuplanai.com
Password: [Generated during deployment]
```

#### Backend Admin UI (admin.docuplanai.com)
```
Admin User:
Email: admin@docuplanai.com
Password: [Generated during deployment]
```

#### Database Access
```
Database Name: pmtool
Database User: pmtool
Database Password: [Generated during deployment]
Host: localhost
Port: 5432
```

#### CalDAV Access
```
URL: https://docuplanai.com/caldav
Username: caldav
Password: [Generated during deployment]
Host: localhost
Port: 5232
SSL: false
```

#### API Documentation
```
Swagger UI: https://admin.docuplanai.com/docs
ReDoc: https://admin.docuplanai.com/redoc
```

### Environment Variables

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
DATABASE_NAME=pmtool
DATABASE_USER=pmtool
DATABASE_PASSWORD=__DB_PASSWORD__  # Generated during deployment
DATABASE_HOST=__DB_HOST__

# Redis Configuration
REDIS_HOST=__REDIS_HOST__
REDIS_PORT=6379
REDIS_PASSWORD=__REDIS_PASSWORD__  # Generated during deployment
REDIS_SSL=false

# CalDAV Configuration
CALDAV_HOST=__CALDAV_HOST__
CALDAV_PORT=5232
CALDAV_SSL=false
CALDAV_PUBLIC_URL=https://docuplanai.com/caldav
```

#### Security Configuration
```bash
# JWT and Session Security (Generated during deployment)
JWT_SECRET=__JWT_SECRET__
SESSION_SECRET=__SESSION_SECRET__

# Server Configuration
SERVER_IP=__SERVER_IP_DOCUPLANAI__
SERVER_PASSWORD=__SERVER_PASSWORD_DOCUPLANAI__

# Service Configuration
DEBUG=false
ALLOWED_HOSTS='["admin.docuplanai.com", "localhost"]'
CORS_ORIGINS='["https://docuplanai.com", "http://localhost:3000"]'
```

Note: All placeholders with `__VARIABLE__` format will be automatically replaced during deployment by the `prepare_env.sh` script. Never commit actual credentials or `.env` files to version control.

### Troubleshooting Commands

#### Check Service Status
```bash
# Verify all services are running
sudo systemctl status postgresql redis-server radicale docuplanai-backend nginx

# Check service logs
sudo tail -f /var/log/docuplanai/backend.log
sudo tail -f /var/log/docuplanai/backend.error.log
sudo journalctl -u docuplanai-backend -f

# Test service connectivity
curl -I http://localhost:8000/docs  # Backend API
curl -I http://localhost:5232       # CalDAV
redis-cli ping                      # Redis
psql -U pmtool -h localhost -d pmtool -c "\conninfo"  # PostgreSQL
```

#### Verify File Permissions
```bash
# Check ownership and permissions
sudo ls -la /var/www/docuplanai/
sudo ls -la /etc/radicale/
sudo ls -la /var/lib/radicale/collections/

# Fix common permission issues
sudo chown -R www-data:www-data /var/www/docuplanai/
sudo chmod 750 /var/www/docuplanai/{backend,logs}
sudo chmod 755 /var/www/docuplanai/html
```

#### Monitor System Resources
```bash
# Check resource usage
free -h                # Memory usage
df -h                 # Disk space
top -b -n 1          # CPU and process info
netstat -tulpn       # Network ports

# Monitor application
sudo tail -f /var/log/docuplanai/backend.log
sudo journalctl -u docuplanai-backend --since "5 minutes ago"
```

### 2. Service Configuration

#### Configure System User
```bash
# Ensure www-data user exists and has correct permissions
sudo usermod -d /var/www www-data
sudo chown -R www-data:www-data /var/www
```

#### Setup Services

##### Database Setup
```bash
# Run PostgreSQL setup script
sudo ./deploy/setup_postgres.sh

# Verify database setup
sudo -u postgres psql -c "\l" | grep pmtool
sudo -u postgres psql -c "\du" | grep pmtool
```

##### Redis Setup
```bash
# Run Redis setup script
sudo ./deploy/setup_redis.sh

# Verify Redis setup
redis-cli ping
redis-cli INFO | grep role
```

##### CalDAV Setup
```bash
# Run CalDAV setup script
sudo ./deploy/setup_caldav.sh

# Verify CalDAV setup
curl -I http://localhost:5232
systemctl status radicale
```

##### Service Verification
```bash
# Check all service statuses
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status radicale

# Verify service permissions
sudo ls -l /var/www/docuplanai
sudo ls -l /etc/radicale
sudo ls -l /var/lib/radicale

# Check service logs
sudo journalctl -u postgresql
sudo journalctl -u redis-server
sudo journalctl -u radicale
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

### Check Service Status
```bash
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status radicale
sudo systemctl status docuplanai-backend
sudo systemctl status nginx
```

### Test Endpoints
- Frontend: https://docuplanai.com
- Backend: https://admin.docuplanai.com/v1/health

## Troubleshooting

### Common Issues and Solutions

#### 1. Permission Issues
```bash
# Check file ownership and permissions
sudo ls -la /var/www/docuplanai
sudo ls -la /etc/radicale
sudo ls -la /var/lib/radicale
sudo ls -la /var/log/docuplanai

# Fix permissions if needed
sudo chown -R www-data:www-data /var/www/docuplanai
sudo chmod 750 /etc/radicale /var/lib/radicale
sudo chmod 640 /var/www/docuplanai/backend/.env
sudo chmod 755 /var/www/docuplanai/html

# Create required directories
sudo mkdir -p /var/log/docuplanai
sudo chown www-data:www-data /var/log/docuplanai
sudo chmod 750 /var/log/docuplanai

# Verify service permissions
sudo -u www-data systemctl status docuplanai-backend
sudo -u www-data test -r /var/www/docuplanai/backend/.env && echo "Can read .env" || echo "Cannot read .env"
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status and configuration
sudo systemctl status postgresql
sudo cat /etc/postgresql/*/main/postgresql.conf | grep -E 'listen_addresses|port'
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep -E 'pmtool|all'

# Test database connection
sudo -u www-data psql -U pmtool -d pmtool -h localhost -c "\conninfo"
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='pmtool';"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
sudo journalctl -u postgresql --since "1 hour ago"

# Verify database setup
sudo -u postgres psql -c "\l+" | grep pmtool
sudo -u postgres psql -c "\du+" | grep pmtool
sudo -u postgres psql -d pmtool -c "\dx"  # Check extensions
```

#### 3. Redis Connection Issues
```bash
# Check Redis status and configuration
sudo systemctl status redis-server
sudo cat /etc/redis/redis.conf | grep -E 'bind|port|requirepass'

# Test Redis connectivity
redis-cli ping
redis-cli -a "$REDIS_PASSWORD" ping
redis-cli -a "$REDIS_PASSWORD" INFO server
redis-cli -a "$REDIS_PASSWORD" CLIENT LIST

# Monitor Redis activity
redis-cli -a "$REDIS_PASSWORD" MONITOR
sudo tail -f /var/log/redis/redis-server.log

# Check Redis memory usage
redis-cli -a "$REDIS_PASSWORD" INFO memory
redis-cli -a "$REDIS_PASSWORD" MEMORY STATS
```

#### 4. Email Service Issues
```bash
# Verify SendGrid configuration
echo ${#SENDGRID_API_KEY}  # Check key length without exposing it
curl -I https://api.sendgrid.com/v3/mail/send -H "Authorization: Bearer $SENDGRID_API_KEY"

# Test email functionality
curl -X POST https://admin.docuplanai.com/api/v1/test-email -H "Content-Type: application/json" \
     -d '{"to": "test@example.com", "subject": "Test Email", "content": "Test Content"}'

# Check email logs and errors
sudo journalctl -u docuplanai-backend -f | grep -i "email\|sendgrid\|mail"
sudo tail -f /var/log/docuplanai/backend.log | grep -i "email"
sudo tail -f /var/log/mail.log
```

#### 5. CalDAV Synchronization Issues
```bash
# Check Radicale service and configuration
sudo systemctl status radicale
sudo cat /etc/radicale/config | grep -v '^#'
sudo ls -la /var/lib/radicale/collections/

# Test CalDAV connectivity
curl -I http://localhost:5232
curl -u caldav:$CALDAV_PASSWORD https://docuplanai.com/caldav
curl -X PROPFIND -u caldav:$CALDAV_PASSWORD http://localhost:5232/

# Monitor CalDAV activity
sudo tail -f /var/log/radicale/radicale.log
sudo journalctl -u radicale -f

# Check CalDAV storage
sudo -u www-data ls -R /var/lib/radicale/collections/
sudo -u www-data find /var/lib/radicale/collections/ -type f -name "*.ics"
```

#### 6. SSL Certificate Issues
```bash
# Check SSL certificates and configuration
sudo certbot certificates
sudo openssl x509 -in /etc/letsencrypt/live/docuplanai.com/fullchain.pem -text -noout
sudo nginx -t
sudo nginx -T | grep -A 10 "server_name docuplanai.com"

# Test SSL connectivity
curl -vI --resolve docuplanai.com:443:127.0.0.1 https://docuplanai.com
curl -vI --resolve admin.docuplanai.com:443:127.0.0.1 https://admin.docuplanai.com
openssl s_client -connect docuplanai.com:443 -servername docuplanai.com

# Check SSL renewal
sudo certbot renew --dry-run
sudo systemctl status certbot.timer
```

#### 7. Environment Configuration Issues
```bash
# Check environment variables and configuration
sudo -u www-data printenv | grep -E 'DATABASE|REDIS|CALDAV|OPENAI|MOLLIE|SENDGRID'
sudo -u www-data python3 -c "from app.core.config import settings; print(settings.dict())"

# Verify configuration files
sudo find /var/www/docuplanai -name "*.env*" -ls
sudo stat /var/www/docuplanai/backend/.env
sudo stat /var/www/docuplanai/frontend/.env.production

# Monitor application logs
sudo tail -f /var/log/docuplanai/backend.log
sudo tail -f /var/log/docuplanai/backend.error.log
sudo journalctl -u docuplanai-backend -f

# Check system resources
free -h
df -h
top -b -n 1
```

#### 8. Application Startup Issues
```bash
# Check service dependencies
sudo systemctl list-dependencies docuplanai-backend
sudo systemctl status postgresql redis-server radicale docuplanai-backend

# Test backend API
curl -I http://localhost:8000/docs
curl -I https://admin.docuplanai.com/docs

# Monitor application startup
sudo tail -f /var/log/docuplanai/backend.log
sudo journalctl -u docuplanai-backend --since "5 minutes ago"

# Check process status
ps aux | grep -E "uvicorn|nginx|postgres|redis|radicale"
sudo netstat -tlpn | grep -E "8000|5432|6379|5232|80|443"
```

For detailed deployment instructions and advanced troubleshooting, see `DEPLOYMENT.md`.

Note: Always check the application logs at `/var/log/docuplanai/` first when troubleshooting issues, as they often contain the most relevant error messages and stack traces.

For detailed deployment instructions, see `DEPLOYMENT.md`.
