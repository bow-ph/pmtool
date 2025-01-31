from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url
TABLE_PREFIX = "test_" if settings.DEBUG else ""

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@event.listens_for(Base.metadata, 'before_create')
def _prefix_tables(target, connection, **kw):
    for table in target.tables.values():
        if not table.name.startswith(TABLE_PREFIX):
            table.name = f"{TABLE_PREFIX}{table.name}"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
