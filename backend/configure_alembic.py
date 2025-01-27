import os
from dotenv import load_dotenv

load_dotenv()

def configure_alembic():
    db_url = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_SERVER")}/{os.getenv("POSTGRES_DB")}'
    
    with open('alembic.ini', 'r') as f:
        config = f.read()
    
    config = config.replace('sqlalchemy.url = driver://user:pass@localhost/dbname', f'sqlalchemy.url = {db_url}')
    
    with open('alembic.ini', 'w') as f:
        f.write(config)

if __name__ == "__main__":
    configure_alembic()
