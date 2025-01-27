from app.core.database import engine
from sqlalchemy import inspect, text

def check_schema():
    inspector = inspect(engine)
    print('\nTable: packages')
    print('Columns:')
    for column in inspector.get_columns('packages'):
        print(f'- {column["name"]}: {column["type"]}')

if __name__ == "__main__":
    check_schema()
