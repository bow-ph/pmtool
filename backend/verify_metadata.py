from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import engine, Base
from app.models.package import Package

def verify_metadata():
    # Create a new metadata instance
    metadata = MetaData()
    
    # Explicitly define the packages table
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
    
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    metadata.create_all(bind=engine)
    
    print("Metadata verification complete. Tables recreated.")

if __name__ == "__main__":
    verify_metadata()
