from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, registry
from app.core.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.database_url

# Create engine with connection pooling and debugging
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True,
    future=True
)

# Create registry and metadata
mapper_registry = registry()
metadata = mapper_registry.metadata

# Create base class
Base = mapper_registry.generate_base()

# Create scoped session factory
session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)
SessionLocal = scoped_session(session_factory)

# Explicitly define packages table
packages = Table(
    'packages',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('description', String, nullable=False),
    Column('price', Float, nullable=False),
    Column('interval', String, nullable=False),
    Column('trial_days', Integer, nullable=True),
    Column('max_projects', Integer, nullable=False),
    Column('features', ARRAY(String), nullable=False),
    Column('button_text', String, nullable=False),
    Column('is_active', Boolean, nullable=False, default=True),
    Column('sort_order', Integer, nullable=True, default=0)
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        SessionLocal.remove()  # Clear session from registry
