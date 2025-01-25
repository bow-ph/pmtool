#!/bin/bash
set -e

# Source environment variables if they exist
if [ -f .env ]; then
    source .env
fi

# Default values (will be overridden by environment variables if set)
CALDAV_HOST=${CALDAV_HOST:-"localhost"}
CALDAV_PORT=${CALDAV_PORT:-5232}
CALDAV_SSL=${CALDAV_SSL:-"false"}

# Install Radicale and dependencies
echo "Installing Radicale and dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
sudo pip3 install radicale

# Create Radicale configuration directory
sudo mkdir -p /etc/radicale
sudo mkdir -p /var/lib/radicale/collections
sudo mkdir -p /var/log/radicale

# Create Radicale configuration
cat > /tmp/radicale.conf << EOL
[server]
hosts = ${CALDAV_HOST}:${CALDAV_PORT}
max_connections = 20
max_content_length = 100000000
timeout = 30
ssl = ${CALDAV_SSL}

[auth]
type = htpasswd
htpasswd_filename = /etc/radicale/users
htpasswd_encryption = bcrypt

[storage]
filesystem_folder = /var/lib/radicale/collections
hook = git

[logging]
level = info
mask_passwords = True

[headers]
Access-Control-Allow-Origin = https://docuplanai.com
Access-Control-Allow-Methods = GET, HEAD, OPTIONS, PROPFIND, PROPPATCH, PUT, DELETE, REPORT, MKCOL, MOVE, COPY
Access-Control-Allow-Headers = User-Agent, Content-Type, Authorization, Depth, If-Match, If-None-Match, Lock-Token, Timeout, Destination
Access-Control-Expose-Headers = Etag, Dav
EOL

# Move configuration file to proper location
sudo mv /tmp/radicale.conf /etc/radicale/config

# Create systemd service file
cat > /tmp/radicale.service << EOL
[Unit]
Description=Radicale CalDAV Server
After=network.target
Requires=network.target

[Service]
Type=simple
User=www-data
Group=www-data
Environment=PYTHONPATH=/var/www/docuplanai/backend
Environment=RADICALE_CONFIG=/etc/radicale/config
Environment=CALDAV_HOST=${CALDAV_HOST}
Environment=CALDAV_PORT=${CALDAV_PORT}
Environment=CALDAV_SSL=${CALDAV_SSL}
ExecStart=/usr/bin/radicale --config /etc/radicale/config
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Move service file to proper location
sudo mv /tmp/radicale.service /etc/systemd/system/radicale.service

# Set proper permissions
sudo chown -R www-data:www-data /etc/radicale
sudo chown -R www-data:www-data /var/lib/radicale
sudo chown -R www-data:www-data /var/log/radicale
sudo chmod 750 /etc/radicale
sudo chmod 750 /var/lib/radicale
sudo chmod 750 /var/log/radicale

# Create default user if not exists
if [ ! -f /etc/radicale/users ]; then
    # Generate random password for default user
    CALDAV_PASS=$(openssl rand -hex 16)
    echo "Creating default CalDAV user..."
    echo "caldav:$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'$CALDAV_PASS', bcrypt.gensalt()).decode())")" | sudo tee /etc/radicale/users
    echo "Default CalDAV credentials:"
    echo "Username: caldav"
    echo "Password: $CALDAV_PASS"
    
    # Save CalDAV user credentials to environment file if it doesn't exist
    if [ ! -f .env ]; then
        echo "CALDAV_USER=caldav" >> .env
        echo "CALDAV_PASSWORD=$CALDAV_PASS" >> .env
    fi
fi

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable radicale
sudo systemctl restart radicale

echo "Radicale CalDAV server setup completed!"
echo "Service status:"
systemctl status radicale --no-pager

# Save CalDAV configuration to environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "CALDAV_HOST=$CALDAV_HOST" >> .env
    echo "CALDAV_PORT=$CALDAV_PORT" >> .env
    echo "CALDAV_SSL=$CALDAV_SSL" >> .env
    echo "CALDAV_PUBLIC_URL=https://docuplanai.com/caldav" >> .env
fi

echo "CalDAV configuration:"
echo "Host: $CALDAV_HOST"
echo "Port: $CALDAV_PORT"
echo "SSL: $CALDAV_SSL"
fi
