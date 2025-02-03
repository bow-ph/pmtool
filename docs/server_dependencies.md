# DocuPlanAI Server Dependencies

## Core System Requirements
- Ubuntu 20.04 LTS or newer
- Python 3.12 (via pyenv)
- Node.js 18+ (via nvm)
- PostgreSQL 16
- Redis (latest stable)
- Nginx (for SSL and CORS handling)

## System Packages
```bash
apt-get update && apt-get install -y \
  build-essential \
  curl \
  git \
  python3-dev \
  python3-pip \
  libpq-dev \
  postgresql \
  postgresql-contrib \
  redis-server \
  nginx \
  certbot \
  python3-certbot-nginx \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  libxml2-dev \
  libxmlsec1-dev \
  libffi-dev \
  liblzma-dev
```

## Installation Order
1. System Packages (as listed above)
2. Python 3.12 via pyenv:
   ```bash
   curl https://pyenv.run | bash
   pyenv install 3.12
   pyenv global 3.12
   ```

3. Node.js via nvm:
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 18
   nvm use 18
   ```

4. PostgreSQL Setup:
   ```bash
   sudo -u postgres createuser bow
   sudo -u postgres createdb bow_db
   sudo -u postgres psql -c "ALTER USER bow WITH PASSWORD 'bow';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bow_db TO bow;"
   ```

5. Redis Setup:
   ```bash
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

6. Python Dependencies:
   ```bash
   cd /var/www/docuplanai/backend
   pip install -r requirements.txt
   ```

7. Node.js Dependencies:
   ```bash
   cd /var/www/docuplanai/frontend
   npm install
   ```

## Environment Variables
Required environment variables (to be set in /var/www/docuplanai/backend/.env):
- OPENAI_API_KEY
- MOLLIE_TEST_API_KEY
- MOLLIE_LIVE_API_KEY
- SENDGRID_API_KEY
- JWT_SECRET
- SESSION_SECRET
- DATABASE_URL
- FRONTEND_URL
- BACKEND_URL

## Service Configuration

### PostgreSQL
- Location: /etc/postgresql/16/main/postgresql.conf
- Authentication: /etc/postgresql/16/main/pg_hba.conf
- Ensure listen_addresses = '*' for network access

### Redis
- Configuration: /etc/redis/redis.conf
- Default port: 6379
- No authentication required for local connections

### Nginx
- Configuration: /etc/nginx/sites-available/docuplanai.conf
- SSL certificates: Managed by Certbot
- CORS headers: Configured in Nginx (not application)

## Development Commands
Frontend:
```bash
cd /var/www/docuplanai/frontend
npm run dev  # Development
npm run build  # Production
```

Backend:
```bash
cd /var/www/docuplanai/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
