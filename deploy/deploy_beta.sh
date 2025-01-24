#!/bin/bash
set -e

# Initialize variables
DEPLOY_PATH="/var/www/docuplanai"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

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

# Verify all required variables are present
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Missing required environment variable: $var"
        exit 1
    fi
done

# Generate secure passwords and secrets
DB_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)

# Create secure temporary credentials file
CREDS_FILE=$(mktemp)
trap "rm -f $CREDS_FILE" EXIT

# Store credentials securely
cat > "$CREDS_FILE" << EOL
OPENAI_API_KEY=$Open_AI_API
MOLLIE_TEST_API_KEY=$Mollie___Test_API_Key
MOLLIE_LIVE_API_KEY=$Mollie___Live_API_Key
SENDGRID_API_KEY=$Sendgrid___DocuPlanAI
DB_PASSWORD=$DB_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
JWT_SECRET=$JWT_SECRET
SESSION_SECRET=$SESSION_SECRET
SERVER_IP=$Server_IP_docuplanai
SERVER_PASSWORD=$Passwort_docuplanai
EOL
chmod 600 "$CREDS_FILE"
# Source credentials
source "$CREDS_FILE"

# Create backend environment from template
cp "$SCRIPT_DIR/config.template.env" backend/.env

# Define environment variable replacements
declare -A env_vars=(
    ["__OPENAI_API_KEY__"]="$OPENAI_API_KEY"
    ["__MOLLIE_TEST_API_KEY__"]="$MOLLIE_TEST_API_KEY"
    ["__MOLLIE_LIVE_API_KEY__"]="$MOLLIE_LIVE_API_KEY"
    ["__SENDGRID_API_KEY__"]="$SENDGRID_API_KEY"
    ["__DB_PASSWORD__"]="$DB_PASSWORD"
    ["__REDIS_PASSWORD__"]="$REDIS_PASSWORD"
    ["__JWT_SECRET__"]="$JWT_SECRET"
    ["__SESSION_SECRET__"]="$SESSION_SECRET"
    ["__SERVER_IP_DOCUPLANAI__"]="$SERVER_IP"
    ["__SERVER_PASSWORD_DOCUPLANAI__"]="$SERVER_PASSWORD"
    ["__DB_HOST__"]="localhost"
    ["__REDIS_HOST__"]="localhost"
    ["__CALDAV_HOST__"]="localhost"
    ["__DEBUG__"]="False"
    ["__ALLOWED_HOSTS__"]="admin.docuplanai.com,localhost"
    ["__CORS_ORIGINS__"]="https://docuplanai.com,http://localhost:3000"
)

# Replace environment variables with proper escaping
for key in "${!env_vars[@]}"; do
    escaped_value=$(echo "${env_vars[$key]}" | sed 's/[\/&]/\\&/g')
    sed -i "s|$key|$escaped_value|g" backend/.env
done

# Set proper permissions
chmod 600 backend/.env

echo "Environment configuration completed successfully"

# Setup SSH configuration
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo -e "Host docuplanai\n  HostName $SERVER_IP\n  User root\n  IdentityFile ~/.ssh/docuplanai_deploy\n  StrictHostKeyChecking no" > ~/.ssh/config
chmod 600 ~/.ssh/config

# Create deployment directories
ssh docuplanai "mkdir -p $DEPLOY_PATH/{html,backend} && \
    chown -R www-data:www-data $DEPLOY_PATH && \
    chmod -R 750 $DEPLOY_PATH"

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

# Configure services
ssh docuplanai "systemctl stop docuplanai-backend && \
    chown -R www-data:www-data /var/www/docuplanai && \
    chmod -R 750 /var/www/docuplanai && \
    systemctl start docuplanai-backend && \
    systemctl restart nginx"

echo "Beta deployment completed successfully!"
echo
echo "Generated credentials (SAVE THESE SECURELY):"
echo "----------------------------------------"
echo "Database password: $DB_PASSWORD"
echo "Redis password: $REDIS_PASSWORD"
echo "JWT secret: $JWT_SECRET"
echo "Session secret: $SESSION_SECRET"
echo "----------------------------------------"
echo
echo "Please save these credentials in a secure password manager."
