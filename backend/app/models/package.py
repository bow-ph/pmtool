from sqlalchemy import Column, Integer, String, Float, Boolean, ARRAY
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, Optional
from app.core.database import Base, packages

class Package(Base):
    __table__ = packages
    
    # Add relationship
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="package")

    def __repr__(self):
        return f"<Package(name='{self.name}', price={self.price}, trial_days={self.trial_days})>"
