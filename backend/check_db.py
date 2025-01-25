from app.core.config import settings
from sqlalchemy import create_engine, text
import sys

def check_database_connection():
    print("=== Database Configuration ===")
    print(f"Database URL: {settings.database_url}")
    
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            print("Successfully connected to database!")
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"PostgreSQL version: {version}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_database_connection()
