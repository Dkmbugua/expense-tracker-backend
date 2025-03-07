from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from models.user import User
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

# ✅ Token blocklist (temporary storage for logout)
BLOCKLIST = set()

def register_user(username, password):
    """Registers a new user and hashes their password"""
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

def login_user(username, password):
    """Logs in a user and returns JWT token"""
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "username": user.username}
    }), 200

@jwt_required()
def logout_user():
    """Logs out a user by adding the token to a blocklist"""
    jti = get_jwt()["jti"]  # Get JWT token identifier
    BLOCKLIST.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200

def is_token_revoked(jwt_payload):
    """Check if a JWT is in the blocklist"""
    return jwt_payload["jti"] in BLOCKLIST
