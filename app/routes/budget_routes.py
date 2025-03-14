# File: app/routes/budget_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.budget_goal import BudgetGoal  # ✅ Correct import
from models.user import User  # ✅ Correct import
from app.db import db  # ✅ Ensure db is imported

budget_routes = Blueprint("budget_routes", __name__)

@budget_routes.route("/set-budget-goal", methods=["POST"])
@jwt_required()
def set_goal():
    """Allow user to set a budget goal for a specific month"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not all(key in data for key in ["amount", "description", "month", "year"]):
        return jsonify({"message": "Amount, description, month, and year are required"}), 400

    goal = BudgetGoal(user_id=user_id, amount=data["amount"], description=data["description"], month=data["month"], year=data["year"])
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({"message": f"Budget goal for {data['month']}/{data['year']} set successfully!"}), 200

@budget_routes.route("/get-budget-goal", methods=["GET"])
@jwt_required()
def get_goal():
    """Retrieve a user's budget goal for a specific month"""
    user_id = get_jwt_identity()
    month = request.args.get("month")
    year = request.args.get("year")

    goal = BudgetGoal.query.filter_by(user_id=user_id, month=month, year=year).first()
    if not goal:
        return jsonify({"message": f"No budget goal set for {month}/{year}."}), 404

    return jsonify(goal.to_dict())
