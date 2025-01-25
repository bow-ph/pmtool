#!/bin/bash
set -e

# Install required packages
apt-get update
apt-get install -y postgresql redis-server python3-venv nginx

# Setup PostgreSQL
sudo -u postgres psql << EOF
CREATE DATABASE pmtool;
CREATE USER pmtool WITH PASSWORD '\${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE pmtool TO pmtool;
EOF

# Setup Redis
cat > /etc/redis/redis.conf << EOF
bind 127.0.0.1
port 6379
daemonize yes
supervised systemd
requirepass \${REDIS_PASSWORD}
EOF

# Setup Radicale
apt-get install -y python3-pip
pip3 install radicale
mkdir -p /etc/radicale
cat > /etc/radicale/config << EOF
[server]
hosts = 0.0.0.0:5232
[auth]
type = htpasswd
htpasswd_filename = /etc/radicale/users
htpasswd_encryption = bcrypt
[storage]
filesystem_folder = /var/lib/radicale/collections
[rights]
type = owner_only
EOF

# Create Radicale systemd service
cat > /etc/systemd/system/radicale.service << EOF
[Unit]
Description=Radicale CalDAV server
After=network.target
Requires=network.target

[Service]
ExecStart=/usr/local/bin/radicale --config /etc/radicale/config
Restart=on-failure
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
EOF

# Create directories and set permissions
mkdir -p /var/lib/radicale/collections
chown -R www-data:www-data /var/lib/radicale
chmod -R 750 /var/lib/radicale

# Enable and start services
systemctl daemon-reload
systemctl enable postgresql redis-server radicale
systemctl restart postgresql redis-server radicale

echo "Services setup completed successfully!"
