# File: app/services/ai_service.py
import os
import random
import spacy
import pickle
import base64
import io
import matplotlib.pyplot as plt
from flask import jsonify
from models.expenses import Expense  # ✅ Ensure correct import
from models.income import Income  # ✅ Ensure correct import
from models.user import User  # ✅ Ensure correct import
from models.budget_goal import BudgetGoal  # ✅ Ensure correct import
from app.db import db  # ✅ Ensure correct import
from datetime import datetime, timedelta

# ✅ Load Trained AI Model
nlp = spacy.load("chatbot_model")

# ✅ Load Responses Mapping
with open("responses.pkl", "rb") as file:
    responses = pickle.load(file)

def chatbot_response(user_input):
    """Fetch chatbot response based on user input"""
    doc = nlp(user_input)
    predicted_intent = max(doc.cats, key=doc.cats.get)

    for intent in responses:
        if intent["tag"] == predicted_intent:
            return random.choice(intent["responses"])

    return "I don't have an answer for that."

# ✅ Financial Analysis Function
def analyze_spending(user_id, timeframe="monthly"):
    """Analyze user spending trends for a given timeframe"""
    now = datetime.utcnow()
    timeframes = {
        "daily": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "weekly": now - timedelta(days=7),
        "monthly": now - timedelta(days=30),
    }
    start_time = timeframes.get(timeframe, now - timedelta(days=30))

    user = User.query.get(user_id)
    user_name = user.username if user else "User"

    expenses = Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_time).all()
    incomes = Income.query.filter(Income.user_id == user_id, Income.date >= start_time).all()

    if not expenses and not incomes:
        return {
            "greeting": f"Hello {user_name} 👋, no transactions found for {timeframe}.",
            "chart": None
        }

    total_spent = sum(exp.amount for exp in expenses)
    total_earned = sum(inc.amount for inc in incomes)
    savings = total_earned - total_spent

    category_spend = {}
    for exp in expenses:
        category_spend[exp.category] = category_spend.get(exp.category, 0) + exp.amount

    # ✅ FIX: Ensure `category_spend` always has at least one entry
    if not category_spend:
        category_spend = {"No transactions": 1}

    top_category = max(category_spend, key=category_spend.get)

    # ✅ Generate Expense Breakdown Chart
    img = io.BytesIO()
    plt.figure(figsize=(8, 4))
    plt.bar(category_spend.keys(), category_spend.values(), color='blue')
    plt.xlabel("Categories")
    plt.ylabel("Spending (KSH)")
    plt.title("Expense Breakdown")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    encoded_img = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return {
        "greeting": f"Hello {user_name} 👋, here's your financial breakdown:",
        "total_income": total_earned,
        "total_expenses": total_spent,
        "savings": savings,
        "top_category": top_category,
        "chart": f"data:image/png;base64,{encoded_img}"
    }


# ✅ Budgeting Assistant Function
def generate_budget_plan(user_id):
    """Generate budget recommendations using the 50/30/20 rule"""
    user = User.query.get(user_id)
    user_name = user.username if user else "User"

    # Retrieve user income and expenses
    incomes = Income.query.filter(Income.user_id == user_id).all()
    expenses = Expense.query.filter(Expense.user_id == user_id).all()

    total_income = sum(inc.amount for inc in incomes)
    total_expenses = sum(exp.amount for exp in expenses)
    savings = total_income - total_expenses

    if total_income == 0:
        return jsonify({"message": "No income found! Please add income data."})

    # Apply the 50/30/20 Rule
    needs_budget = total_income * 0.50  # Essentials like rent, food, bills
    wants_budget = total_income * 0.30  # Entertainment, shopping
    savings_budget = total_income * 0.20  # Savings and investments

    return {
        "greeting": f"Hello {user_name} 👋, here's your personalized budget plan:",
        "total_income": total_income,
        "total_expenses": total_expenses,
        "savings": savings,
        "budget_plan": {
            "Needs (50%)": needs_budget,
            "Wants (30%)": wants_budget,
            "Savings (20%)": savings_budget
        }
    }

# ✅ Set Budget Goal
def set_budget_goal(user_id, amount, description, month, year):
    """Save a user's budget goal for a specific month."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        goal = BudgetGoal(user_id=user_id, amount=amount, description=description, month=month, year=year)
        db.session.add(goal)
        db.session.commit()
        return jsonify({"message": "Budget goal set successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


# ✅ Get Budget Goal
def get_budget_goal(user_id, month, year):
    """Retrieve user's budget goal for a specific month."""
    goal = BudgetGoal.query.filter_by(user_id=user_id, month=month, year=year).first()
    if not goal:
        return jsonify({"message": f"No budget goal set for {month}/{year}."}), 404

    return {
        "goal_amount": goal.amount,
        "description": goal.description,
        "month": goal.month,
        "year": goal.year
    }

# ✅ Track Budget Progress
def track_budget_progress(user_id):
    """Check how much of the budget goal has been reached."""
    goal = BudgetGoal.query.filter_by(user_id=user_id).order_by(BudgetGoal.id.desc()).first()
    if not goal:
        return {"message": "No budget goal found"}

    incomes = Income.query.filter_by(user_id=user_id).all()
    total_income = sum(inc.amount for inc in incomes)

    progress_percentage = (total_income / goal.amount) * 100 if goal.amount > 0 else 0

    return {
        "goal_amount": goal.amount,
        "current_savings": total_income,
        "progress": round(progress_percentage, 2)
    }
