#!/bin/bash

# Create .env file from template
cp config.template.env .env

# Update API keys and secrets from environment variables
if [ -n "$Open_AI_API" ]; then
    sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$Open_AI_API|g" .env
fi

if [ -n "$Mollie___Test_API_Key" ]; then
    sed -i "s|MOLLIE_TEST_API_KEY=.*|MOLLIE_TEST_API_KEY=$Mollie___Test_API_Key|g" .env
fi

if [ -n "$Mollie___Live_API_Key" ]; then
    sed -i "s|MOLLIE_LIVE_API_KEY=.*|MOLLIE_LIVE_API_KEY=$Mollie___Live_API_Key|g" .env
fi

if [ -n "$Sendgrid___DocuPlanAI" ]; then
    sed -i "s|SENDGRID_API_KEY=.*|SENDGRID_API_KEY=$Sendgrid___DocuPlanAI|g" .env
fi

# Generate a secure JWT secret
JWT_SECRET=$(openssl rand -hex 32)
sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|g" .env

# Set secure database password
DB_PASSWORD=$(openssl rand -hex 16)
sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|g" .env

echo "Environment configuration prepared successfully!"
