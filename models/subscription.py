from app.db import db  # Import database instance
from datetime import datetime
from sqlalchemy.orm import relationship

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)  
    next_payment_date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ Define relationship with User model with correct `back_populates`
    user = relationship("User", back_populates="subscriptions")

    def to_dict(self):
        """Convert subscription model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "amount": self.amount,
            "billing_cycle": self.billing_cycle,
            "next_payment_date": self.next_payment_date.strftime("%Y-%m-%d %H:%M:%S") if self.next_payment_date else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Subscription {self.name} - {self.amount} KSH>"
