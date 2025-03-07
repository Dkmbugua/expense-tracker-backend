from app.db import db

class Income(db.Model):
    __tablename__ = "income"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # User who created the expense
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Convert model instance to dictionary for easy JSON response"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S")
        }
