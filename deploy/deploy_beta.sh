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

# Generate secure passwords
DB_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
JWT_SECRET=$(openssl rand -hex 32)

# Create deployment directories and set permissions
ssh docuplanai "mkdir -p $DEPLOY_PATH/{html,backend} && \
    chown -R www-data:www-data $DEPLOY_PATH && \
    chmod -R 750 $DEPLOY_PATH"

# Prepare backend environment
echo "Preparing backend environment..."
cp deploy/config.template.env backend/.env
sed -i "s/__OPENAI_API_KEY__/$Open_AI_API/g" backend/.env
sed -i "s/__MOLLIE_TEST_API_KEY__/$Mollie___Test_API_Key/g" backend/.env
sed -i "s/__MOLLIE_LIVE_API_KEY__/$Mollie___Live_API_Key/g" backend/.env
sed -i "s/__SENDGRID_API_KEY__/$Sendgrid___DocuPlanAI/g" backend/.env
sed -i "s/__DB_PASSWORD__/$DB_PASSWORD/g" backend/.env
sed -i "s/__REDIS_PASSWORD__/$REDIS_PASSWORD/g" backend/.env
sed -i "s/__JWT_SECRET__/$JWT_SECRET/g" backend/.env

# Build and deploy frontend
cd frontend
npm install
npm run build:prod
rsync -avz --delete dist/ docuplanai:$DEPLOY_PATH/html/

# Deploy backend
cd ../backend
rsync -avz --delete --exclude '.env' --exclude 'venv' . docuplanai:$DEPLOY_PATH/backend/
scp .env docuplanai:$DEPLOY_PATH/backend/.env

# Setup backend environment and services
ssh docuplanai "cd $DEPLOY_PATH/backend && \
    python3 -m venv venv && \
    chown -R www-data:www-data venv && \
    sudo -u www-data /var/www/docuplanai/backend/venv/bin/pip install -r requirements.txt && \
    sudo -u www-data /var/www/docuplanai/backend/venv/bin/pip install alembic && \
    sudo -u www-data PYTHONPATH=/var/www/docuplanai/backend /var/www/docuplanai/backend/venv/bin/alembic upgrade head && \
    systemctl restart docuplanai-backend nginx redis-server postgresql && \
    systemctl enable docuplanai-backend nginx redis-server postgresql"

# Configure services for www-data
ssh docuplanai "systemctl stop docuplanai-backend && \
    chown -R www-data:www-data /var/www/docuplanai && \
    chmod -R 750 /var/www/docuplanai && \
    systemctl start docuplanai-backend"

echo "Beta deployment completed successfully!"
echo "Generated credentials:"
echo "Database password: $DB_PASSWORD"
echo "Redis password: $REDIS_PASSWORD"
echo "Please save these credentials securely."
