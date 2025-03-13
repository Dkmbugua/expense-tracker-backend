import os
import random
import spacy
import pickle
import base64
import io
import matplotlib.pyplot as plt
from flask import jsonify
from models.expenses import Expense
from models.income import Income
from models.user import User
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

    # ✅ Select a random response
    for intent in responses:
        if intent["tag"] == predicted_intent:
            return random.choice(intent["responses"])

    return "I don't have an answer for that."

# ✅ Financial Analysis Function
def analyze_spending(user_id, timeframe="monthly", user_prompt=""):
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
        return jsonify({
            "greeting": f"Hello {user_name} 👋, no transactions found for {timeframe}.",
            "chart": None
        })

    total_spent = sum(exp.amount for exp in expenses)
    total_earned = sum(inc.amount for inc in incomes)
    savings = total_earned - total_spent

    category_spend = {}
    for exp in expenses:
        category_spend[exp.category] = category_spend.get(exp.category, 0) + exp.amount
    top_category = max(category_spend, key=category_spend.get) if category_spend else "No category"

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

    # ✅ Generate AI Financial Advice
    advice = chatbot_response(f"Advice for {user_name} with savings {savings}")

    return {
        "greeting": f"Hello {user_name} 👋, here's your financial breakdown:",
        "total_income": total_earned,
        "total_expenses": total_spent,
        "savings": savings,
        "top_category": top_category,
        "advice": advice,
        "chart": f"data:image/png;base64,{encoded_img}"  # ✅ Embed the chart directly
    }
