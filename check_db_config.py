from app.core.config import settings
from app.core.database import SessionLocal, engine
from sqlalchemy import text

def check_database_config():
    print("\n=== Database Configuration ===")
    print(f"Database URL: {settings.database_url}")
    print(f"Database Name: {settings.DATABASE_NAME}")
    print(f"Database Host: {settings.DATABASE_HOST}")
    
    print("\n=== Testing Connection ===")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection error: {str(e)}")

if __name__ == "__main__":
    check_database_config()
