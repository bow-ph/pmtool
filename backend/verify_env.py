from app.core.config import settings

print('\nVerifying environment variables...')
print(f'DATABASE_NAME: {settings.DATABASE_NAME}')
print(f'DATABASE_USER: {settings.DATABASE_USER}')
print(f'DATABASE_PASSWORD: {"*" * len(settings.DATABASE_PASSWORD) if settings.DATABASE_PASSWORD else "Not set"}')
print(f'DATABASE_HOST: {settings.DATABASE_HOST}')
print(f'OPENAI_API_KEY: {"*" * 10}{settings.OPENAI_API_KEY[-5:] if settings.OPENAI_API_KEY else "Not set"}')
print(f'MOLLIE_TEST_API_KEY: {"*" * 10}{settings.MOLLIE_TEST_API_KEY[-5:] if settings.MOLLIE_TEST_API_KEY else "Not set"}')
print(f'MOLLIE_LIVE_API_KEY: {"*" * 10}{settings.MOLLIE_LIVE_API_KEY[-5:] if settings.MOLLIE_LIVE_API_KEY else "Not set"}')
print(f'SENDGRID_API_KEY: {"*" * 10}{settings.SENDGRID_API_KEY[-5:] if settings.SENDGRID_API_KEY else "Not set"}')
print(f'JWT_SECRET: {"*" * len(settings.JWT_SECRET) if settings.JWT_SECRET else "Not set"}')
print(f'SESSION_SECRET: {"*" * len(settings.SESSION_SECRET) if settings.SESSION_SECRET else "Not set"}')
