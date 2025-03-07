from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import db
from models.user import User
from datetime import timedelta

auth_routes = Blueprint("auth_routes", __name__, url_prefix="/api/auth")

# ✅ User Registration (Signup)
@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data.get("username") or not data.get("password"):
        return jsonify({"message": "Username and password are required"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ✅ User Login
@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
    return jsonify({"access_token": access_token, "user": {"id": user.id, "username": user.username}}), 200


# ✅ Logout - Revoke JWT
@auth_routes.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response, 200


# ✅ Protected Route - Requires Authentication
@auth_routes.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": "You have access!", "user_id": current_user}), 200


# ✅ API Test Route
@auth_routes.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Auth route is working!"}), 200
