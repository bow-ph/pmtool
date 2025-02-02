from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import settings

class Task(Base):
    __tablename__ = "test_tasks" if settings.DEBUG else "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("test_projects.id" if settings.DEBUG else "projects.id"))
    title = Column(String)
    description = Column(String)
    estimated_hours = Column(Float)
    actual_hours = Column(Float, nullable=True)
    status = Column(String)  # pending, in_progress, completed
    priority = Column(String, nullable=True)  # high, medium, low
    confidence_score = Column(Float)  # AI confidence in the estimate (0-1)
    confidence_rationale = Column(String)  # Detailed explanation of confidence score
    hourly_rate = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # CalDAV integration
    caldav_event_uid = Column(String, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title or self.description or "Untitled Task",
            "description": self.description,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "duration_hours": self.duration_hours,
            "hourly_rate": self.hourly_rate,
            "status": self.status or "pending",
            "priority": self.priority or "medium",
            "confidence_score": self.confidence_score,
            "confidence_rationale": self.confidence_rationale,
            "project_id": self.project_id,
            "caldav_event_uid": self.caldav_event_uid,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        # Always include confidence field for test compatibility
        task_dict["confidence"] = self.confidence_score
        return task_dict
