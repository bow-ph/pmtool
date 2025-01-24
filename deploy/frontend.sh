#!/bin/bash

# Build frontend
cd /home/ubuntu/repos/pmtool/frontend
npm install
npm run build:prod

# Create nginx configuration
cat > /tmp/docuplanai.conf << 'EOL'
server {
    listen 80;
    server_name docuplanai.com;
    root /var/www/docuplanai/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://admin.docuplanai.com;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOL

# Deploy frontend
rsync -avz --delete dist/ root@116.202.15.157:/var/www/docuplanai/html/
scp /tmp/docuplanai.conf root@116.202.15.157:/etc/nginx/sites-available/docuplanai.conf

# Configure nginx
ssh root@116.202.15.157 "ln -sf /etc/nginx/sites-available/docuplanai.conf /etc/nginx/sites-enabled/ && \
    nginx -t && \
    systemctl reload nginx"
