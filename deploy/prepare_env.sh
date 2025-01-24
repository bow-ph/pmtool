#!/bin/bash
set -e

# Create .env file from template
cp config.template.env .env

# Generate secure passwords and secrets
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

echo "Updating environment configuration..."

# API Keys
if [ -n "$Open_AI_API" ]; then
    sed -i "s|__OPENAI_API_KEY__|$Open_AI_API|g" .env
fi

if [ -n "$Mollie___Test_API_Key" ]; then
    sed -i "s|__MOLLIE_TEST_API_KEY__|$Mollie___Test_API_Key|g" .env
fi

if [ -n "$Mollie___Live_API_Key" ]; then
    sed -i "s|__MOLLIE_LIVE_API_KEY__|$Mollie___Live_API_Key|g" .env
fi

if [ -n "$Sendgrid___DocuPlanAI" ]; then
    sed -i "s|__SENDGRID_API_KEY__|$Sendgrid___DocuPlanAI|g" .env
fi

# Service Configuration
sed -i "s|__DB_HOST__|localhost|g" .env
sed -i "s|__DB_PASSWORD__|$DB_PASSWORD|g" .env
sed -i "s|__REDIS_HOST__|localhost|g" .env
sed -i "s|__REDIS_PASSWORD__|$REDIS_PASSWORD|g" .env
sed -i "s|__CALDAV_HOST__|localhost|g" .env
sed -i "s|__JWT_SECRET__|$JWT_SECRET|g" .env
sed -i "s|__SESSION_SECRET__|$SESSION_SECRET|g" .env

# Application Configuration
sed -i "s|__DEBUG__|False|g" .env
sed -i "s|__ALLOWED_HOSTS__|admin.docuplanai.com,localhost|g" .env
sed -i "s|__CORS_ORIGINS__|https://docuplanai.com,http://localhost:3000|g" .env

echo "Environment configuration prepared successfully!"
echo
echo "Generated credentials:"
echo "Database password: $DB_PASSWORD"
echo "Redis password: $REDIS_PASSWORD"
echo "JWT secret: $JWT_SECRET"
echo "Session secret: $SESSION_SECRET"
echo
echo "Please save these credentials securely."
