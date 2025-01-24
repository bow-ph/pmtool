#!/bin/bash
set -e

# Initialize variables
DEPLOY_PATH="/var/www/docuplanai"

# Check for required environment variables
echo "Checking environment variables..."
if [ -z "$Open_AI_API" ] || [ -z "$Mollie___Test_API_Key" ] || [ -z "$Mollie___Live_API_Key" ] || [ -z "$Sendgrid___DocuPlanAI" ]; then
    echo "Error: Missing required API keys"
    exit 1
fi

# Setup SSH configuration
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo -e "Host docuplanai\n  HostName 116.202.15.157\n  User root\n  IdentityFile ~/.ssh/docuplanai_deploy\n  StrictHostKeyChecking no" > ~/.ssh/config
chmod 600 ~/.ssh/docuplanai_deploy

# Update environment configuration
echo "Updating environment configuration..."
cp deploy/config.template.env backend/.env
sed -i "s/__OPENAI_API_KEY__/$Open_AI_API/g" backend/.env
sed -i "s/__MOLLIE_TEST_API_KEY__/$Mollie___Test_API_Key/g" backend/.env
sed -i "s/__MOLLIE_LIVE_API_KEY__/$Mollie___Live_API_Key/g" backend/.env
sed -i "s/__SENDGRID_API_KEY__/$Sendgrid___DocuPlanAI/g" backend/.env

# Create deployment directories
ssh docuplanai "mkdir -p $DEPLOY_PATH/{html,backend}"

# Build and deploy frontend
cd frontend
npm install
npm run build:prod
rsync -avz --delete dist/ docuplanai:$DEPLOY_PATH/html/

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
rsync -avz --delete --exclude '.env' . docuplanai:$DEPLOY_PATH/backend/
scp .env docuplanai:$DEPLOY_PATH/backend/.env

# Setup services
ssh docuplanai "cd $DEPLOY_PATH/backend && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt && \
    alembic upgrade head && \
    systemctl restart docuplanai-backend nginx redis-server postgresql && \
    systemctl enable docuplanai-backend nginx redis-server postgresql"

echo "Beta deployment completed successfully!"
