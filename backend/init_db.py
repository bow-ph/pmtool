from app.core.database import Base, engine
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from sqlalchemy.orm import Session
from app.core.config import settings

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    db = Session(engine)
    try:
        # Create test user if not exists
        test_user = db.query(User).filter(User.email == "admin@pmtool.test").first()
        if not test_user:
            test_user = User(
                email="admin@pmtool.test",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMxRHHJ.m",  # Password: test123
                is_active=True,
                is_superuser=True,
                subscription_type="enterprise"
            )
            db.add(test_user)
            db.flush()

        # Create test project if not exists
        test_project = db.query(Project).filter(Project.id == 1).first()
        if not test_project:
            test_project = Project(
                id=1,
                user_id=test_user.id,
                name="Test Project",
                description="A test project for development"
            )
            db.add(test_project)
        
        db.commit()
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
