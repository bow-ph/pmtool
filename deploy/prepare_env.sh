#!/bin/bash

# Create .env file from template
cp config.template.env .env

# Update API keys and secrets from environment variables
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

# Server Configuration
if [ -n "$Server_IP_docuplanai" ]; then
    sed -i "s|__SERVER_IP_DOCUPLANAI__|$Server_IP_docuplanai|g" .env
fi

if [ -n "$Passwort_docuplanai" ]; then
    sed -i "s|__SERVER_PASSWORD_DOCUPLANAI__|$Passwort_docuplanai|g" .env
fi

# Set service hosts
sed -i "s|__REDIS_HOST__|localhost|g" .env
sed -i "s|__CALDAV_HOST__|localhost|g" .env
sed -i "s|__DB_HOST__|localhost|g" .env

# Generate secure passwords and secrets
JWT_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

# Update configuration with generated values
sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|g" .env
sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|g" .env
sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=$REDIS_PASSWORD|g" .env

echo "Environment configuration prepared successfully!"
echo "Generated passwords:"
echo "Database password: $DB_PASSWORD"
echo "Redis password: $REDIS_PASSWORD"
