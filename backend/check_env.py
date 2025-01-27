import os
from dotenv import load_dotenv

load_dotenv()

required_vars = {
    'POSTGRES_SERVER': os.getenv('POSTGRES_SERVER'),
    'POSTGRES_USER': os.getenv('POSTGRES_USER'),
    'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'POSTGRES_DB': os.getenv('POSTGRES_DB'),
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'JWT_SECRET': os.getenv('JWT_SECRET'),
    'SESSION_SECRET': os.getenv('SESSION_SECRET'),
    'SENDGRID_API_KEY': os.getenv('SENDGRID_API_KEY'),
    'MOLLIE_TEST_API_KEY': os.getenv('MOLLIE_TEST_API_KEY'),
    'MOLLIE_LIVE_API_KEY': os.getenv('MOLLIE_LIVE_API_KEY'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'FRONTEND_URL': os.getenv('FRONTEND_URL'),
    'BACKEND_URL': os.getenv('BACKEND_URL')
}

print('\nEnvironment Variable Status:')
for var, value in required_vars.items():
    status = '✓' if value else '✗'
    print(f'{var}: {status} {"(set)" if value else "(missing)"}')

# Check if values match expected format
if required_vars['FRONTEND_URL']:
    if not required_vars['FRONTEND_URL'].startswith('http://'):
        print(f"\nWarning: FRONTEND_URL should use HTTP protocol")

if required_vars['BACKEND_URL']:
    if not required_vars['BACKEND_URL'].startswith('http://'):
        print(f"\nWarning: BACKEND_URL should use HTTP protocol")

# Verify database connection
try:
    from sqlalchemy import create_engine
    db_url = f"postgresql://{required_vars['POSTGRES_USER']}:{required_vars['POSTGRES_PASSWORD']}@{required_vars['POSTGRES_SERVER']}/{required_vars['POSTGRES_DB']}"
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("\nDatabase connection: ✓ Successful")
except Exception as e:
    print(f"\nDatabase connection: ✗ Failed - {str(e)}")
