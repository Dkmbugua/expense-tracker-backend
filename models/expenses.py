from app.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) 

    user = relationship("User", back_populates="expenses")

    # ✅ FIXED: Correctly indented function
    def to_dict(self):
        """Convert model instance to dictionary for easy JSON response"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S") if self.date else None,
        }
