# DocuPlanAI Setup Guide

## Default Access Credentials

### Frontend (https://docuplanai.com)
```
Admin User:
Email: admin@docuplanai.com
Password: admin123

Test User:
Email: test@docuplanai.com
Password: test123
```

### Backend Admin UI (https://admin.docuplanai.com)
```
Admin User:
Email: admin@docuplanai.com
Password: admin123
```

Note: Change these default passwords immediately after first login.

## Quick Start Guide

### 1. Environment Variables
Create a `.env` file with the following variables:
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
MOLLIE_TEST_API_KEY=your_mollie_test_key
MOLLIE_LIVE_API_KEY=your_mollie_live_key
SENDGRID_API_KEY=your_sendgrid_api_key

# Database
DB_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_secure_redis_password
```

### 2. Setup Services
```bash
# Run setup script
sudo ./deploy/setup_services.sh
```

### 3. Deploy Application
```bash
# Deploy backend and frontend
./deploy/deploy_beta.sh
```

## Service Verification

### Check Service Status
```bash
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status radicale
sudo systemctl status docuplanai-backend
sudo systemctl status nginx
```

### Test Endpoints
- Frontend: https://docuplanai.com
- Backend: https://admin.docuplanai.com/v1/health

## Troubleshooting

### Common Issues
1. **Database Connection**
   - Check PostgreSQL status
   - Verify database credentials in `.env`

2. **Redis Connection**
   - Check Redis status
   - Verify Redis password in `.env`

3. **Email Service**
   - Verify SendGrid API key
   - Check email logs

For detailed deployment instructions, see `DEPLOYMENT.md`.
