from app.db import db  # ✅ Import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")  
    income = relationship("Income", back_populates="user", cascade="all, delete-orphan")  
    budget_goals = relationship("BudgetGoal", back_populates="user", cascade="all, delete-orphan")

    # ❌ Remove duplicate `subscriptions` reference
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the password"""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        
    def check_password(self, password):
        """Checks the hashed password"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user model to dictionary"""
        return {
            "id": self.id,
            "username": self.username
        }
