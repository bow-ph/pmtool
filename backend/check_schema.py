from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_schema():
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    
    print('\nTables:', inspector.get_table_names())
    print('\nColumns in packages table:')
    for column in inspector.get_columns('packages'):
        print(f'- {column["name"]}: {column["type"]}')

if __name__ == "__main__":
    check_schema()
