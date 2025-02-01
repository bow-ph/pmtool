import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent)
sys.path.append(backend_dir)

from app.core.database import SessionLocal
from app.models.user import User
from app.core.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        user = User(
            email='admin@pmtool.test',
            hashed_password=get_password_hash('pmtool'),
            is_active=True,
            subscription_type='trial'
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

if __name__ == '__main__':
    create_test_user()
