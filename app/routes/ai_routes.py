from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_service import analyze_spending, chatbot_response, generate_budget_plan
from app.db import db
from models.budget_goal import BudgetGoal  # Import BudgetGoal model

ai_routes = Blueprint("ai_routes", __name__)

# ✅ AI Insights Route
@ai_routes.route("/ai-insights", methods=["GET", "POST"])
@jwt_required()
def ai_insights():
    """Handles AI financial analysis."""
    user_id = get_jwt_identity()

    if request.method == "GET":
        timeframe = request.args.get("timeframe", "monthly")
        insights = analyze_spending(user_id, timeframe)
        return jsonify(insights), 200

    elif request.method == "POST":
        data = request.get_json()
        prompt_text = data.get("prompt", "")

        if not prompt_text:
            return jsonify({"error": "Prompt is required!"}), 400

        insights = analyze_spending(user_id, "monthly", prompt_text)
        return jsonify(insights), 200

# ✅ AI Chatbot Route
@ai_routes.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot responses."""
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required!"}), 400

    response = chatbot_response(user_input)
    return jsonify({"response": response}), 200

# ✅ AI Budget Plan Route
@ai_routes.route("/budget-plan", methods=["GET"])
@jwt_required()
def budget_plan():
    """Generates budget recommendations using the 50/30/20 rule."""
    user_id = get_jwt_identity()
    budget = generate_budget_plan(user_id)
    return jsonify(budget), 200

# ✅ Set Budget Goal Route
@ai_routes.route("/set-budget-goal", methods=["POST"])
@jwt_required()
def set_budget_goal():
    """Set a budget goal for a specific month and year."""
    user_id = get_jwt_identity()
    data = request.json

    amount = data.get("amount")
    description = data.get("description")
    month = data.get("month")
    year = data.get("year")

    if not amount or not description or not month or not year:
        return jsonify({"error": "All fields are required"}), 400

    try:
        existing_goal = BudgetGoal.query.filter_by(user_id=user_id, month=month, year=year).first()
        if existing_goal:
            existing_goal.amount = amount
            existing_goal.description = description
        else:
            new_goal = BudgetGoal(user_id=user_id, amount=amount, description=description, month=month, year=year)
            db.session.add(new_goal)

        db.session.commit()
        return jsonify({"message": "Budget goal set successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to set budget goal: {str(e)}"}), 500

# ✅ Get Budget Goal Route
@ai_routes.route("/get-budget-goal", methods=["GET"])
@jwt_required()
def get_budget_goal():
    """Fetch the user's budget goal for a specific month and year."""
    user_id = get_jwt_identity()
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    if not month or not year:
        return jsonify({"error": "Month and year are required"}), 400

    budget_goal = BudgetGoal.query.filter_by(user_id=user_id, month=month, year=year).first()

    if not budget_goal:
        return jsonify({"message": "No budget goal set for this month."}), 404

    return jsonify({
        "amount": budget_goal.amount,
        "description": budget_goal.description,
        "month": budget_goal.month,
        "year": budget_goal.year
    }), 200
