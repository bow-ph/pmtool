from sqlalchemy import inspect, MetaData, Table, Column, Integer, String, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_model():
    from sqlalchemy import create_engine
    
    # Create engine with debug logging
    engine = create_engine(settings.database_url, echo=True)
    
    # Create new metadata and base
    metadata = MetaData()
    Base = declarative_base(metadata=metadata)
    
    # Define Package model explicitly
    class Package(Base):
        __tablename__ = 'packages'
        __table_args__ = {'extend_existing': True}
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        description = Column(String, nullable=False)
        price = Column(Float, nullable=False)
        interval = Column(String, nullable=False)
        trial_days = Column(Integer, nullable=True)
        max_projects = Column(Integer, nullable=False)
        features = Column(ARRAY(String), nullable=False)
        button_text = Column(String, nullable=False)
        is_active = Column(Boolean, nullable=False, default=True)
        sort_order = Column(Integer, nullable=True, default=0)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Reflect existing table
        inspector = inspect(engine)
        columns = inspector.get_columns('packages')
        logger.info("Existing columns in database:")
        for column in columns:
            logger.info(f"Column: {column['name']}, Type: {column['type']}")
        
        # Try to query the table
        logger.info("\nAttempting to query packages table:")
        packages = session.query(Package).filter(Package.is_active == True).all()
        for package in packages:
            logger.info(f"Package: {package.name}, Trial Days: {package.trial_days}")
        
        logger.info("Model verification successful")
        return True
    except Exception as e:
        logger.error(f"Error during model verification: {str(e)}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    verify_model()
