import requests
import os
from flask_jwt_extended import get_jwt_identity
from app.db import db
from models.expenses import Expense
from models.income import Income
from models.user import User  # ✅ Ensure we fetch user details
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def analyze_spending(user_id, timeframe="monthly", user_prompt=""):
    """AI-powered financial insights, customized for different user types."""

    now = datetime.utcnow()
    timeframes = {
        "daily": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "weekly": now - timedelta(days=7),
        "monthly": now - timedelta(days=30),
    }
    start_time = timeframes.get(timeframe, now - timedelta(days=30))

    # ✅ Fetch user info
    user = User.query.get(user_id)
    user_name = user.name if user else "User"
    user_type = user.user_type if user and user.user_type else "General"  # Student, Adult, Entrepreneur, Parent

    # ✅ Fetch transactions
    expenses = Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_time).all()
    incomes = Income.query.filter(Income.user_id == user_id, Income.date >= start_time).all()

    if not expenses and not incomes:
        return {"message": f"Hello {user_name}, no transactions found for {timeframe}."}

    # ✅ Compute totals
    total_spent = sum(exp.amount for exp in expenses)
    total_earned = sum(inc.amount for inc in incomes)

    # ✅ Find top spending category
    category_spend = {}
    for exp in expenses:
        category_spend[exp.category] = category_spend.get(exp.category, 0) + exp.amount
    top_category = max(category_spend, key=category_spend.get) if category_spend else "No category"

    # ✅ Predict future spending
    prev_month_expenses = Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_time - timedelta(days=30)).all()
    prev_month_spent = sum(exp.amount for exp in prev_month_expenses)
    growth_rate = ((total_spent - prev_month_spent) / prev_month_spent) if prev_month_spent > 0 else 0.05
    predicted_next_month_spending = round(total_spent * (1 + growth_rate), 2)

    # ✅ Format AI response based on user type
    user_advice = {
        "Student": "💡 As a student, consider saving on transport by using public transit and looking for student discounts.",
        "Adult": "💡 Managing household expenses? Try meal planning and reducing impulse purchases.",
        "Entrepreneur": "💡 Looking to grow your business? Consider setting aside 20% of revenue for investments.",
        "Parent": "💡 Family budgeting is key! Try using savings envelopes for different expenses.",
        "General": "💡 Always track your expenses and aim to save at least 10% of your income.",
    }

    # ✅ AI Prompt
    prompt = f"""
    Hello {user_name}, based on your spending:
    - Total Income: KSH {total_earned}
    - Total Expenses: KSH {total_spent}
    - Top Spending Category: {top_category}
    
    {user_advice.get(user_type, user_advice["General"])}
    {user_prompt} Please respond in bullet points.
    """

    # ✅ Call AI API
    response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        return {"message": "AI service unavailable"}

    ai_response = response.json()[0]["generated_text"]
    ai_response = " ".join(ai_response.split())  # Clean whitespace

    # ✅ Savings Breakdown Data
    savings_breakdown = [{"category": k, "amount": v} for k, v in category_spend.items()]

    # ✅ Follow-up Questions
    follow_ups = [
        "How can I improve my savings?",
        "What’s the best way to reduce transport costs?",
        "Can you suggest a budgeting strategy?"
    ]

    return {
        "greeting": f"Hello {user_name} 👋, here's your financial breakdown:",
        "total_spent": total_spent,
        "total_earned": total_earned,
        "top_category": top_category,
        "predicted_next_month_spending": predicted_next_month_spending,
        "ai_insights": ai_response,
        "savings_breakdown": savings_breakdown,
        "trend_data": [
            {"name": "Last Month", "spending": prev_month_spent, "savings": total_earned - prev_month_spent},
            {"name": "This Month", "spending": total_spent, "savings": total_earned - total_spent},
            {"name": "Next Month (Predicted)", "spending": predicted_next_month_spending, "savings": total_earned - predicted_next_month_spending}
        ],
        "follow_ups": follow_ups
    }
