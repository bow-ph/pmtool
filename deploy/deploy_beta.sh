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

# Create deployment directories and set permissions (as root)
sudo mkdir -p $DEPLOY_PATH/{html,backend}
sudo chown -R www-data:www-data $DEPLOY_PATH
sudo chmod -R 750 $DEPLOY_PATH
sudo usermod -d /var/www www-data

# Prepare backend environment
echo "Preparing backend environment..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cp "$SCRIPT_DIR/config.template.env" backend/.env
sed -i "s|__OPENAI_API_KEY__|$Open_AI_API|g" backend/.env
sed -i "s|__MOLLIE_TEST_API_KEY__|$Mollie___Test_API_Key|g" backend/.env
sed -i "s|__MOLLIE_LIVE_API_KEY__|$Mollie___Live_API_Key|g" backend/.env
sed -i "s|__SENDGRID_API_KEY__|$Sendgrid___DocuPlanAI|g" backend/.env
sed -i "s|__DB_PASSWORD__|$DB_PASSWORD|g" backend/.env
sed -i "s|__REDIS_PASSWORD__|$REDIS_PASSWORD|g" backend/.env
sed -i "s|__JWT_SECRET__|$JWT_SECRET|g" backend/.env
sed -i "s|__DB_HOST__|localhost|g" backend/.env
sed -i "s|__REDIS_HOST__|localhost|g" backend/.env
sed -i "s|__CALDAV_HOST__|localhost|g" backend/.env
sed -i "s|__DEBUG__|False|g" backend/.env
sed -i "s|__ALLOWED_HOSTS__|admin.docuplanai.com,localhost|g" backend/.env
sed -i "s|__CORS_ORIGINS__|https://docuplanai.com,http://localhost:3000|g" backend/.env

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
cd $DEPLOY_PATH/backend
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
sudo -u www-data bash -c 'source venv/bin/activate && \
    pip install -r requirements.txt && \
    pip install alembic && \
    PYTHONPATH=/var/www/docuplanai/backend alembic upgrade head'
sudo systemctl restart docuplanai-backend nginx redis-server postgresql
sudo systemctl enable docuplanai-backend nginx redis-server postgresql

# Configure services and permissions
sudo systemctl stop docuplanai-backend
sudo chown -R www-data:www-data /var/www/docuplanai
sudo chmod -R 750 /var/www/docuplanai
sudo find /var/www/docuplanai -type d -exec chmod 750 {} \;
sudo find /var/www/docuplanai -type f -exec chmod 640 {} \;
sudo systemctl start docuplanai-backend
sudo systemctl restart nginx

echo "Beta deployment completed successfully!"
echo "Generated credentials:"
echo "Database password: $DB_PASSWORD"
echo "Redis password: $REDIS_PASSWORD"
echo "Please save these credentials securely."
