from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.project import Project

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
    
    def can_create_project(self, user_id: int) -> bool:
        """Check if user can create a new project based on their subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            return False
            
        # Check if subscription is expired
        if subscription.end_date and subscription.end_date < datetime.now():
            return False
            
        # Get current project count
        project_count = self.db.query(Project).filter(
            Project.user_id == user_id,
            Project.created_at >= subscription.start_date
        ).count()
        
        # Check limits based on package type
        if subscription.package_type == "trial":
            return project_count < 1
        elif subscription.package_type == "team":
            return project_count < 10
        elif subscription.package_type == "enterprise":
            return project_count < (subscription.project_limit or float('inf'))
            
        return False
    
    def get_package_duration(self, package_type: str, custom_months: Optional[int] = None) -> timedelta:
        """Get subscription duration based on package type"""
        if package_type in ["trial", "team"]:
            return timedelta(days=90)  # 3 months
        elif package_type == "enterprise" and custom_months:
            return timedelta(days=custom_months * 30.44)  # Average month length
        else:
            raise ValueError("Invalid package type or missing custom duration")
