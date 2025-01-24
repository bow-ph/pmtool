#!/bin/bash
set -e

# Initialize variables
SERVER_IP="116.202.15.157"
DEPLOY_PATH="/var/www/docuplanai"

# Create deployment directories
ssh root@$SERVER_IP "mkdir -p $DEPLOY_PATH/{html,backend}"

# Build and deploy frontend
cd frontend
npm install
npm run build:prod
rsync -avz --delete dist/ root@$SERVER_IP:$DEPLOY_PATH/html/

# Build and deploy backend
cd ../backend
python -m pip install -r requirements.txt
alembic upgrade head

# Create environment file from template
cp ../deploy/config.template.env .env

# Update environment variables
sed -i "s/__OPENAI_API_KEY__/$Open_AI_API/g" .env
sed -i "s/__MOLLIE_TEST_API_KEY__/$Mollie___Test_API_Key/g" .env
sed -i "s/__MOLLIE_LIVE_API_KEY__/$Mollie___Live_API_Key/g" .env
sed -i "s/__SENDGRID_API_KEY__/$Sendgrid___DocuPlanAI/g" .env

# Deploy backend files
rsync -avz --delete --exclude '.env' . root@$SERVER_IP:$DEPLOY_PATH/backend/
scp .env root@$SERVER_IP:$DEPLOY_PATH/backend/.env

# Setup services
ssh root@$SERVER_IP "cd $DEPLOY_PATH/backend && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt && \
    alembic upgrade head && \
    systemctl restart docuplanai-backend nginx redis-server postgresql && \
    systemctl enable docuplanai-backend nginx redis-server postgresql"

echo "Beta deployment completed successfully!"
