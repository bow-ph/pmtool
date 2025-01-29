from sqlalchemy import create_engine, inspect, text
from app.core.database import Base
from app.core.config import settings
from app.models import User, Package, Subscription, Invoice, Project, Task

# Connect to test database and create tables
engine = create_engine(f"postgresql://pmtool:{settings.DATABASE_PASSWORD}@localhost/pmtool?client_encoding=utf8", echo=True)

# Override table names to use prefixes
for table in Base.metadata.tables.values():
    table.schema = None
    table.name = f"test_{table.name}"

print("\nRegistered models in Base.metadata:", Base.metadata.tables.keys())
print("\nAttempting to create all tables...")
Base.metadata.create_all(bind=engine)

# Verify tables were created
inspector = inspect(engine)
tables = inspector.get_table_names()
print("\nCreated tables:", tables)

for table in ['users', 'projects', 'tasks', 'packages', 'subscriptions', 'invoices']:
    if table not in tables:
        print(f"\nWARNING: {table} table was not created!")
        print("Available tables:", tables)
