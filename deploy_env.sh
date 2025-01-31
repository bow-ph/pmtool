#!/bin/bash
cat > /var/www/docuplanai/backend/.env << EOF
OPENAI_API_KEY=$1
MOLLIE_TEST_API_KEY=$2
MOLLIE_LIVE_API_KEY=$3
SENDGRID_API_KEY=$4
DATABASE_NAME=docuplanai
DATABASE_USER=docuplanai
DATABASE_PASSWORD=docuplanai_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=false
CALDAV_HOST=localhost
CALDAV_PORT=5232
CALDAV_SSL=false
CALDAV_PUBLIC_URL=https://docuplanai.com/caldav
FRONTEND_URL=https://docuplanai.com
BACKEND_URL=https://admin.docuplanai.com
EMAILS_FROM_EMAIL=noreply@docuplanai.com
EMAILS_FROM_NAME=DocuPlanAI
JWT_SECRET=your-jwt-secret-key
SESSION_SECRET=your-session-secret-key
DEBUG=true
ALLOWED_HOSTS=["admin.docuplanai.com","localhost"]
CORS_ORIGINS=["https://docuplanai.com","http://localhost:3000"]
EOF

chown www-data:www-data /var/www/docuplanai/backend/.env
chmod 600 /var/www/docuplanai/backend/.env
systemctl restart docuplanai-backend
sleep 5
journalctl -u docuplanai-backend -n 50 --no-pager
