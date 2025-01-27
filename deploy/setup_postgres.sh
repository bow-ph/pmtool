#!/bin/bash
set -e

# Source environment variables if they exist
if [ -f .env ]; then
    source .env
fi

# Default values (will be overridden by environment variables if set)
DATABASE_NAME=${DATABASE_NAME:-"pmtool"}
DATABASE_USER=${DATABASE_USER:-"pmtool"}
DATABASE_PASSWORD=${DATABASE_PASSWORD:-"pmtool"}
DATABASE_HOST=${DATABASE_HOST:-"localhost"}

# Install PostgreSQL if not already installed
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
fi

# Ensure PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

# Create database user and set password
echo "Creating database user..."
sudo -u postgres psql -v ON_ERROR_STOP=1 << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DATABASE_USER') THEN
        CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD' CREATEDB;
    ELSE
        ALTER USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';
        ALTER USER $DATABASE_USER WITH CREATEDB;
    END IF;
END
\$\$;
EOF

# Update pg_hba.conf to allow password authentication
echo "Configuring PostgreSQL authentication..."
sudo sed -i 's/local.*all.*all.*peer/local   all             all                                     md5/' /etc/postgresql/*/main/pg_hba.conf
sudo sed -i 's/host.*all.*all.*127.0.0.1\/32.*ident/host    all             all             127.0.0.1\/32            md5/' /etc/postgresql/*/main/pg_hba.conf

# Update pg_hba.conf to allow password authentication
echo "Configuring PostgreSQL authentication..."
sudo sed -i 's/local.*all.*all.*peer/local   all             all                                     md5/' /etc/postgresql/*/main/pg_hba.conf
sudo sed -i 's/host.*all.*all.*127.0.0.1\/32.*ident/host    all             all             127.0.0.1\/32            md5/' /etc/postgresql/*/main/pg_hba.conf

# Create database
echo "Creating database..."
sudo -u postgres psql -v ON_ERROR_STOP=1 << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DATABASE_NAME') THEN
        CREATE DATABASE $DATABASE_NAME;
    END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;
\c $DATABASE_NAME

-- Set up extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set default privileges
ALTER DEFAULT PRIVILEGES FOR USER $DATABASE_USER IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $DATABASE_USER;
ALTER DEFAULT PRIVILEGES FOR USER $DATABASE_USER IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO $DATABASE_USER;
EOF

# Configure PostgreSQL for remote connections if needed
if [ "$DATABASE_HOST" != "localhost" ]; then
    echo "Configuring PostgreSQL for remote connections..."
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf
    
    # Add entry to pg_hba.conf if not already present
    HBA_CONF="/etc/postgresql/*/main/pg_hba.conf"
    if ! sudo grep -q "host $DATABASE_NAME $DATABASE_USER" $HBA_CONF; then
        echo "host $DATABASE_NAME $DATABASE_USER all md5" | sudo tee -a $HBA_CONF
    fi
    
    # Restart PostgreSQL to apply changes
    sudo systemctl restart postgresql
fi

# Run database migrations
echo "Running database migrations..."
cd /var/www/docuplanai/backend
source venv/bin/activate
alembic upgrade head

echo "PostgreSQL setup completed successfully!"
echo "Database configuration:"
echo "Database name: $DATABASE_NAME"
echo "Database user: $DATABASE_USER"
echo "Database password: $DATABASE_PASSWORD"
echo "Database host: $DATABASE_HOST"

# Save database configuration to environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "DATABASE_NAME=$DATABASE_NAME" >> .env
    echo "DATABASE_USER=$DATABASE_USER" >> .env
    echo "DATABASE_PASSWORD=$DATABASE_PASSWORD" >> .env
    echo "DATABASE_HOST=$DATABASE_HOST" >> .env
fi
