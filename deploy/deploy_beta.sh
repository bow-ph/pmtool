#!/bin/bash
set -e

# Initialize variables
DEPLOY_PATH="/var/www/docuplanai"

# Check for required environment variables
echo "Checking environment variables..."
required_vars=(
    "Open_AI_API"
    "Mollie___Test_API_Key"
    "Mollie___Live_API_Key"
    "Sendgrid___DocuPlanAI"
    "Server_IP_docuplanai"
    "Passwort_docuplanai"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Missing required environment variable: $var"
        exit 1
    fi
done

# Setup SSH configuration
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo -e "Host docuplanai\n  HostName ${Server_IP_docuplanai}\n  User root\n  IdentityFile ~/.ssh/docuplanai_deploy\n  StrictHostKeyChecking no" > ~/.ssh/config
chmod 600 ~/.ssh/docuplanai_deploy

# Prepare environment configuration
echo "Preparing environment configuration..."
./deploy/prepare_env.sh

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
