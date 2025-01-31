#!/bin/bash

echo "=== Verifying Frontend ==="
curl -s http://docuplanai.com/ | grep -q "frontend" && echo "✓ Frontend accessible" || echo "✗ Frontend not accessible"

echo -e "\n=== Verifying Backend Health ==="
curl -s http://admin.docuplanai.com/api/v1/health | grep -q "ok" && echo "✓ Backend health check passed" || echo "✗ Backend health check failed"

echo -e "\n=== Verifying API Endpoints ==="
endpoints=(
  "/api/v1/tasks"
  "/api/v1/packages/"
  "/api/v1/projects/1/proactive-hints"
  "/api/v1/admin/users"
  "/api/v1/admin/subscriptions"
  "/api/v1/admin/invoices"
)

for endpoint in "${endpoints[@]}"; do
  response=$(curl -s -w "%{http_code}" http://admin.docuplanai.com$endpoint)
  http_code=${response: -3}
  if [[ $http_code == "200" || $http_code == "401" ]]; then
    echo "✓ $endpoint - OK (Status: $http_code)"
  else
    echo "✗ $endpoint - Failed (Status: $http_code)"
  fi
done

echo -e "\n=== Verifying Database Connection ==="
cd /var/www/docuplanai/backend
source venv/bin/activate
PYTHONPATH=/var/www/docuplanai/backend python3 /tmp/verify_db.py

echo -e "\n=== Verifying Nginx Configuration ==="
nginx -t

echo -e "\n=== Service Status ==="
systemctl status docuplanai-backend --no-pager
systemctl status nginx --no-pager
