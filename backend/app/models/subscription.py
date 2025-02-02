from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
from datetime import datetime

class Subscription(Base):
    __tablename__ = "test_subscriptions" if settings.DEBUG else "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("test_users.id" if settings.DEBUG else "users.id"))
    mollie_id = Column(String, unique=True, index=True)
    customer_id = Column(String)
    package_id = Column(Integer, ForeignKey("test_packages.id" if settings.DEBUG else "packages.id"))
    package_type = Column(String)  # trial, team, enterprise
    project_limit = Column(Integer, nullable=True)  # Custom limit for enterprise packages
    status = Column(String)  # active, pending, canceled, suspended
    amount = Column(Float)
    interval = Column(String)  # 3 months, 6 months, 12 months
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_date = Column(DateTime, nullable=True)

    # Relationships
    invoices = relationship("Invoice", back_populates="subscription")
    user = relationship("User", back_populates="subscriptions")
    package = relationship("Package", back_populates="subscriptions")
