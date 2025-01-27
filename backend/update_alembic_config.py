import os
from app.core.config import settings

def update_alembic_config():
    with open('alembic.ini', 'r') as f:
        config = f.read()

    config = config.replace('sqlalchemy.url = %(DB_URL)s', f'sqlalchemy.url = {settings.database_url}')

    with open('alembic.ini', 'w') as f:
        f.write(config)

if __name__ == "__main__":
    update_alembic_config()
