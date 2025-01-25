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

# Function to handle environment variable replacement
replace_env_var() {
    local var_name=$1
    local env_key=$2
    local env_value=$3
    local required=$4

    if [ -n "$env_value" ]; then
        sed -i "s|__${env_key}__|$env_value|g" .env
        echo "✓ Set $var_name"
    else
        if [ "$required" = "true" ]; then
            echo "⚠️  WARNING: Required $var_name not found in environment"
        else
            echo "ℹ️  Optional $var_name not found, using default"
        fi
    fi
}

echo "Setting up environment variables..."
echo "==================================="

# API Keys (Required)
replace_env_var "OpenAI API Key" "OPENAI_API_KEY" "$Open_AI_API" "true"
replace_env_var "Mollie Test API Key" "MOLLIE_TEST_API_KEY" "$Mollie___Test_API_Key" "true"
replace_env_var "Mollie Live API Key" "MOLLIE_LIVE_API_KEY" "$Mollie___Live_API_Key" "true"
replace_env_var "SendGrid API Key" "SENDGRID_API_KEY" "$Sendgrid___DocuPlanAI" "true"

# Server Configuration (Required for production)
replace_env_var "Server IP" "SERVER_IP_DOCUPLANAI" "$Server_IP_docuplanai" "true"
replace_env_var "Server Password" "SERVER_PASSWORD_DOCUPLANAI" "$Passwort_docuplanai" "true"

echo
echo "Setting up service configurations..."
echo "==================================="

# Database Configuration
sed -i "s|__DB_HOST__|localhost|g" .env
sed -i "s|__DB_PASSWORD__|$DB_PASSWORD|g" .env
echo "✓ Database configuration set"

# Redis Configuration
sed -i "s|__REDIS_HOST__|localhost|g" .env
sed -i "s|__REDIS_PORT__|6379|g" .env
sed -i "s|__REDIS_PASSWORD__|$REDIS_PASSWORD|g" .env
sed -i "s|__REDIS_SSL__|false|g" .env
echo "✓ Redis configuration set"

# CalDAV Configuration
sed -i "s|__CALDAV_HOST__|localhost|g" .env
sed -i "s|__CALDAV_PORT__|5232|g" .env
sed -i "s|__CALDAV_SSL__|false|g" .env
echo "✓ CalDAV configuration set"

# Security Configuration
sed -i "s|__JWT_SECRET__|$JWT_SECRET|g" .env
sed -i "s|__SESSION_SECRET__|$SESSION_SECRET|g" .env
echo "✓ Security configuration set"

# Application Configuration
sed -i "s|__DEBUG__|false|g" .env
sed -i "s|__ALLOWED_HOSTS__|'[\"admin.docuplanai.com\", \"localhost\"]'|g" .env
sed -i "s|__CORS_ORIGINS__|'[\"https://docuplanai.com\", \"http://localhost:3000\"]'|g" .env
echo "✓ Application configuration set"

echo "Environment configuration prepared successfully!"
echo
echo "Generated credentials:"
echo "Database password: $DB_PASSWORD"
echo "Redis password: $REDIS_PASSWORD"
echo "JWT secret: $JWT_SECRET"
echo "Session secret: $SESSION_SECRET"
echo
echo "Please save these credentials securely and update your password manager."
