from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class HintConfirmation(Base):
    __tablename__ = "hint_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    hint_message = Column(String, nullable=False)
    confirmed_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_by = Column(Integer, ForeignKey("users.id"))
