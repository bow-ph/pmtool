from app.core.database import SessionLocal
from app.models.user import User
from app.core.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "admin@pmtool.test").first()
        if not test_user:
            # Create test user
            test_user = User(
                email="admin@pmtool.test",
                hashed_password=get_password_hash("pmtool"),
                is_active=True,
                is_superuser=True,
                subscription_type="enterprise",
                subscription_end_date=None,
                client_type="enterprise",
                company_name="Test Company",
                vat_number="123456789",
                billing_address="Test Address",
                shipping_address="Test Address",
                phone_number="123456789",
                contact_person="Test Person",
                notes="Test user created by init_test_user.py"
            )
            db.add(test_user)
            db.commit()
            print("Test user created successfully")
        else:
            print("Test user already exists")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
