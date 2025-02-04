from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.core.auth import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Create test user if it doesn't exist
if not db.query(User).filter(User.email == 'admin@pmtool.test').first():
    test_user = User(
        email='admin@pmtool.test',
        hashed_password=get_password_hash('pmtool'),
        is_active=True,
        subscription_type='trial'
    )
    db.add(test_user)
    db.commit()
