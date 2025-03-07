from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.expenses import Expense
from app.db import db

expenses_routes = Blueprint("expenses_routes", __name__)

# ✅ Create an expense
@expenses_routes.route("/expenses", methods=["POST"])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get("category") or not data.get("amount"):
        return jsonify({"message": "Category and amount are required"}), 400

    new_expense = Expense(
        user_id=user_id,
        category=data["category"],
        amount=data["amount"],
        description=data.get("description", "")
    )

    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "Expense added successfully", "expense": new_expense.to_dict()}), 201

# ✅ Retrieve all expenses for the logged-in user
@expenses_routes.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    return jsonify([expense.to_dict() for expense in expenses]), 200

# ✅ Retrieve a single expense
@expenses_routes.route("/expenses/<int:expense_id>", methods=["GET"])
@jwt_required()
def get_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    return jsonify(expense.to_dict()), 200

# ✅ Update an expense
@expenses_routes.route("/expenses/<int:expense_id>", methods=["PUT"])
@jwt_required()
def update_expense(expense_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    expense.category = data.get("category", expense.category)
    expense.amount = data.get("amount", expense.amount)
    expense.description = data.get("description", expense.description)

    db.session.commit()

    return jsonify({"message": "Expense updated successfully", "expense": expense.to_dict()}), 200

# ✅ Delete an expense
@expenses_routes.route("/expenses/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "Expense deleted successfully"}), 200
