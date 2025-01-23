from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mollie_id = Column(String, unique=True, index=True)
    customer_id = Column(String)
    package_id = Column(Integer, ForeignKey("packages.id"))
    status = Column(String)  # active, pending, canceled, suspended
    amount = Column(Float)
    interval = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_date = Column(DateTime, nullable=True)

    # Relationships
    invoices = relationship("Invoice", back_populates="subscription")
