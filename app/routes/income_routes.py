from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.income import Income  # ✅ Import Income Model
from app.db import db

income_routes = Blueprint("income_routes", __name__)

# ✅ Create an income entry
@income_routes.route("/income", methods=["POST"])
@jwt_required()
def create_income():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get("category") or not data.get("amount"):
        return jsonify({"message": "Category and amount are required"}), 400

    new_income = Income(
        user_id=user_id,
        category=data["category"],
        amount=data["amount"],
        description=data.get("description", "")
    )

    db.session.add(new_income)
    db.session.commit()

    return jsonify({"message": "Income added successfully", "income": new_income.to_dict()}), 201

# ✅ Retrieve all income records for the logged-in user
@income_routes.route("/income", methods=["GET"])
@jwt_required()
def get_income():
    user_id = get_jwt_identity()
    income_records = Income.query.filter_by(user_id=user_id).all()
    return jsonify([income.to_dict() for income in income_records]), 200

# ✅ Retrieve a single income record
@income_routes.route("/income/<int:income_id>", methods=["GET"])
@jwt_required()
def get_income_entry(income_id):
    user_id = get_jwt_identity()
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return jsonify({"message": "Income record not found"}), 404

    return jsonify(income.to_dict()), 200

# ✅ Update an income record
@income_routes.route("/income/<int:income_id>", methods=["PUT"])
@jwt_required()
def update_income(income_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return jsonify({"message": "Income record not found"}), 404

    income.category = data.get("category", income.category)
    income.amount = data.get("amount", income.amount)
    income.description = data.get("description", income.description)

    db.session.commit()

    return jsonify({"message": "Income updated successfully", "income": income.to_dict()}), 200

# ✅ Delete an income record
@income_routes.route("/income/<int:income_id>", methods=["DELETE"])
@jwt_required()
def delete_income(income_id):
    user_id = get_jwt_identity()
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return jsonify({"message": "Income record not found"}), 404

    db.session.delete(income)
    db.session.commit()

    return jsonify({"message": "Income deleted successfully"}), 200
