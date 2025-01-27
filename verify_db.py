from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.config import settings
from sqlalchemy import text

def verify_database():
    try:
        print(f"\nDatabase configuration:")
        print(f"URL: {settings.database_url}")
        print(f"Name: {settings.DATABASE_NAME}")
        print(f"Host: {settings.DATABASE_HOST}")
        print(f"User: {settings.DATABASE_USER}")
        
        print("\nTesting connection...")
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("Basic connection test: SUCCESS")
            
            # Get table list
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            print("\nAvailable tables:")
            for table in tables:
                print(f"- {table[0]}")
                
        return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False

if __name__ == '__main__':
    verify_database()
