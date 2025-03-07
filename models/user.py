from app.db import db  # ✅ Import db from app.db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    
    def set_password(self, password):
        """Hashes the password with PBKDF2 instead of Scrypt"""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        
    def check_password(self, password):
        """Checks the hashed password"""
        return check_password_hash(self.password_hash, password)
