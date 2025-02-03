# DocuPlanAI Server Configuration Guide

## Environment Variables
Required environment variables in `/var/www/docuplanai/backend/.env`:
```ini
# API Keys
OPENAI_API_KEY=your_openai_api_key
MOLLIE_TEST_API_KEY=your_mollie_test_key
MOLLIE_LIVE_API_KEY=your_mollie_live_key
SENDGRID_API_KEY=your_sendgrid_key

# Security
JWT_SECRET=your_jwt_secret_key
SESSION_SECRET=your_session_secret_key

# Database
DATABASE_URL=postgresql://bow:bow@localhost:5432/bow_db
DATABASE_NAME=bow_db
DATABASE_USER=bow
DATABASE_PASSWORD=bow
DATABASE_HOST=localhost

# URLs
FRONTEND_URL=https://docuplanai.com
BACKEND_URL=https://admin.docuplanai.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

## Nginx Configuration
### Frontend Configuration (/etc/nginx/sites-available/docuplanai.com)
```nginx
server {
    listen 80;
    server_name docuplanai.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name docuplanai.com;

    ssl_certificate /etc/letsencrypt/live/docuplanai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docuplanai.com/privkey.pem;

    root /var/www/docuplanai/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Backend Configuration (/etc/nginx/sites-available/admin.docuplanai.com)
```nginx
server {
    listen 80;
    server_name admin.docuplanai.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name admin.docuplanai.com;

    ssl_certificate /etc/letsencrypt/live/admin.docuplanai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.docuplanai.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # CORS headers (managed by Nginx)
        add_header 'Access-Control-Allow-Origin' 'https://docuplanai.com' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://docuplanai.com' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
}
```

## PostgreSQL Configuration
1. Database Creation:
```sql
CREATE DATABASE bow_db;
CREATE USER bow WITH PASSWORD 'bow';
GRANT ALL PRIVILEGES ON DATABASE bow_db TO bow;
```

2. PostgreSQL Configuration (/etc/postgresql/16/main/postgresql.conf):
```ini
listen_addresses = '*'
max_connections = 100
shared_buffers = 128MB
```

3. Client Authentication (/etc/postgresql/16/main/pg_hba.conf):
```
# TYPE  DATABASE    USER    ADDRESS         METHOD
local   all        all                     md5
host    all        all     127.0.0.1/32    md5
host    all        all     ::1/128         md5
host    bow_db     bow     localhost       md5
```

## Application Configuration

### Initialize Database
```bash
cd /var/www/docuplanai/backend
python -m app.core.init_db
```

### Create Test User
```bash
cd /var/www/docuplanai/backend
python -m app.core.init_test_user
```

### OpenAI Configuration
1. Set environment variable in .env
2. Configure rate limits in openai_service.py:
   - RPM (Requests per Minute): 60
   - TPM (Tokens per Minute): 90,000
   - Max tokens per request: 4,000

### Application Services
1. Backend Service (/etc/systemd/system/docuplanai-backend.service):
```ini
[Unit]
Description=DocuPlanAI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/docuplanai/backend
Environment="PATH=/var/www/docuplanai/backend/venv/bin"
ExecStart=/var/www/docuplanai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

2. Enable and start services:
```bash
sudo systemctl enable docuplanai-backend
sudo systemctl start docuplanai-backend
```

## SSL Certificates
```bash
sudo certbot --nginx -d docuplanai.com -d admin.docuplanai.com
```

## File Permissions
```bash
sudo chown -R www-data:www-data /var/www/docuplanai
sudo chmod -R 755 /var/www/docuplanai
```
