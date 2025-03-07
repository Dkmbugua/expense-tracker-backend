import os

class Config:
    """Configuration settings for the Flask application."""
    
    # Secret keys
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Change this in production!
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecurejwtkey")  # Used for JWT authentication

    # Database settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
