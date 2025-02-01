from app.core.database import SessionLocal
from app.models.user import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("Users in database:")
        for user in users:
            print(f"- {user.email} (active: {user.is_active})")
    finally:
        db.close()

if __name__ == '__main__':
    list_users()
