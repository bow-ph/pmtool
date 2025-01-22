from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    description = Column(String)
    estimated_hours = Column(Float)
    actual_hours = Column(Float, nullable=True)
    status = Column(String)  # pending, in_progress, completed
    confidence_score = Column(Float)  # AI confidence in the estimate (0-1)
