#!/bin/bash
set -e

# Generate Redis password if not provided
if [ -z "$REDIS_PASSWORD" ]; then
    REDIS_PASSWORD=$(openssl rand -hex 16)
fi

# Create Redis configuration from template
envsubst < redis.conf.template > /etc/redis/redis.conf

# Set proper permissions
chown redis:redis /etc/redis/redis.conf
chmod 640 /etc/redis/redis.conf

# Ensure Redis directories exist with proper permissions
mkdir -p /var/lib/redis /var/log/redis
chown redis:redis /var/lib/redis /var/log/redis
chmod 750 /var/lib/redis /var/log/redis

# Restart Redis service
systemctl restart redis-server
systemctl enable redis-server

# Verify Redis is running
if ! systemctl is-active --quiet redis-server; then
    echo "Error: Redis failed to start"
    exit 1
fi

# Test Redis connection
if ! redis-cli ping > /dev/null; then
    echo "Error: Redis is not responding"
    exit 1
fi

echo "Redis configuration completed successfully"
echo "Redis password: $REDIS_PASSWORD"
