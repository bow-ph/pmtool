from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import settings

class Project(Base):
    __tablename__ = "test_projects" if settings.DEBUG else "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("test_users.id" if settings.DEBUG else "users.id"))
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="active")
    is_active = Column(Boolean, default=True)

    # Relationships
    tasks = relationship("Task", back_populates="project")
    user = relationship("User", back_populates="projects")
