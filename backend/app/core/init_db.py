from app.core.database import Base, engine
from app.models.user import User
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.subscription import Subscription
from app.models.package import Package
from app.models.task import Task
from sqlalchemy import inspect

def init_db():
    inspector = inspect(engine)
    if not inspector.has_table("test_users"):
        Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
