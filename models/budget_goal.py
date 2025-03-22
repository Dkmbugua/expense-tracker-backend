from app.db import db  # ✅ Ensure using the correct db instance
from sqlalchemy.orm import relationship
from datetime import datetime

class BudgetGoal(db.Model):
    """Stores user budget goals for specific months"""
    __tablename__ = "budget_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # Stores the month (1-12)
    year = db.Column(db.Integer, nullable=False)  # Stores the year

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Added
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # ✅ Added

    user = relationship("User", back_populates="budget_goals")  

    def to_dict(self):
        """Convert object to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "description": self.description,
            "month": self.month,
            "year": self.year,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
