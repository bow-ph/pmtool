#!/bin/bash

# Build backend
cd /home/ubuntu/repos/pmtool/backend
python -m pip install -r requirements.txt
alembic upgrade head

# Create systemd service file
cat > /tmp/docuplanai-backend.service << 'EOL'
[Unit]
Description=DocuPlanAI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/docuplanai/backend
Environment="PATH=/var/www/docuplanai/backend/venv/bin"
ExecStart=/var/www/docuplanai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Create nginx configuration
cat > /tmp/admin.docuplanai.conf << 'EOL'
server {
    listen 80;
    server_name admin.docuplanai.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOL

# Deploy backend
rsync -avz --delete --exclude '.env' . root@116.202.15.157:/var/www/docuplanai/backend/
scp .env root@116.202.15.157:/var/www/docuplanai/backend/.env
scp /tmp/docuplanai-backend.service root@116.202.15.157:/etc/systemd/system/
scp /tmp/admin.docuplanai.conf root@116.202.15.157:/etc/nginx/sites-available/admin.docuplanai.conf

# Configure services
ssh root@116.202.15.157 "cd /var/www/docuplanai/backend && \
    python -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt && \
    systemctl daemon-reload && \
    systemctl enable docuplanai-backend && \
    systemctl restart docuplanai-backend && \
    ln -sf /etc/nginx/sites-available/admin.docuplanai.conf /etc/nginx/sites-enabled/ && \
    nginx -t && \
    systemctl reload nginx"
