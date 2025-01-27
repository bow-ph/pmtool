import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def check_environment():
    print("\nEnvironment Variables Status:")
    required_vars = [
        "POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
        "SECRET_KEY", "SENDGRID_API_KEY", "SMTP_FROM_EMAIL", "SMTP_FROM_NAME",
        "MOLLIE_TEST_API_KEY", "MOLLIE_LIVE_API_KEY", "MOLLIE_MODE",
        "OPENAI_API_KEY", "CALDAV_USERNAME", "CALDAV_PASSWORD"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        print(f"{var}: {'✓ Set' if value else '✗ Missing'}")

def check_database():
    print("\nDatabase Connection Status:")
    try:
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}/{os.getenv('POSTGRES_DB')}"
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")

if __name__ == "__main__":
    check_environment()
    check_database()
