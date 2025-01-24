#!/bin/bash
set -e

# Generate Redis password
REDIS_PASS=$(openssl rand -hex 16)

# Create Redis configuration
cat > /etc/redis/redis.conf << EOL
# Network
bind 127.0.0.1
port 6379
protected-mode yes

# General
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
logfile /var/log/redis/redis-server.log

# Security
requirepass "${REDIS_PASS}"
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""

# Memory and persistence
dir /var/lib/redis
maxmemory 256mb
maxmemory-policy allkeys-lru
maxclients 100
timeout 300

# Logging
loglevel notice
slowlog-log-slower-than 10000

# Snapshotting
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes

# Security limits
maxmemory-samples 10
EOL

# Set proper permissions
chown redis:redis /etc/redis/redis.conf
chmod 640 /etc/redis/redis.conf

# Ensure Redis directories exist with proper permissions
mkdir -p /var/lib/redis /var/log/redis
chown redis:redis /var/lib/redis /var/log/redis
chmod 750 /var/lib/redis /var/log/redis

# Create systemd override for additional security
mkdir -p /etc/systemd/system/redis-server.service.d
cat > /etc/systemd/system/redis-server.service.d/override.conf << EOL
[Service]
# Security enhancements
ProtectSystem=full
PrivateDevices=yes
ProtectHome=yes
NoNewPrivileges=yes
PrivateTmp=yes
CapabilityBoundingSet=
EOL

# Reload systemd and restart Redis
systemctl daemon-reload
systemctl restart redis-server
systemctl enable redis-server

# Verify Redis is running
if ! systemctl is-active --quiet redis-server; then
    echo "Error: Redis failed to start"
    journalctl -u redis-server --no-pager -n 50
    exit 1
fi

# Test Redis connection
if ! redis-cli -a "${REDIS_PASS}" ping > /dev/null; then
    echo "Error: Redis is not responding"
    exit 1
fi

# Store Redis password in environment file
echo "REDIS_PASSWORD=${REDIS_PASS}" > /etc/redis/.env
chmod 600 /etc/redis/.env
chown redis:redis /etc/redis/.env

echo "Redis configuration completed successfully"
echo "Redis password has been saved to /etc/redis/.env"
echo "Redis password: ${REDIS_PASS}"
