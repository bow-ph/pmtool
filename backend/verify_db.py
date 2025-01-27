from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

# Create a fresh engine with a new connection pool
engine = create_engine("postgresql://pmtool:pmtool_db_password@localhost/pmtool", 
                      pool_pre_ping=True, 
                      pool_recycle=3600)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Test raw SQL query first
    print("\nRaw SQL Test:")
    result = session.execute(text("SELECT * FROM packages LIMIT 1")).fetchone()
    print(result)

    # Import models after confirming connection
    from app.models.package import Package

    # Test ORM query
    print("\nORM Query Test:")
    packages = session.query(Package).filter(Package.is_active == True).order_by(Package.sort_order).all()
    for pkg in packages:
        print(f"Package {pkg.id}: {pkg.name}")

except Exception as e:
    print(f"Error: {str(e)}")
finally:
    session.close()
    engine.dispose()
