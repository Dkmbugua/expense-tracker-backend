import requests
import os
from flask_jwt_extended import get_jwt_identity
from app.db import db
from models.expenses import Expense
from models.income import Income
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def detect_language(text):
    """Detects if the prompt is in Kiswahili."""
    kiswahili_words = ["pesa", "gharama", "bajeti", "matatu", "shilingi", "chakula", "kazi", "shule", "malipo"]
    return any(word in text.lower() for word in kiswahili_words)

def analyze_spending(user_id, timeframe="monthly", user_prompt=""):
    """Fetch AI-powered financial insights & predict trends."""

    now = datetime.utcnow()
    timeframes = {
        "minute": now - timedelta(minutes=60),
        "daily": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "weekly": now - timedelta(days=7),
        "monthly": now - timedelta(days=30),
    }
    start_time = timeframes.get(timeframe, now - timedelta(days=30))

    # ✅ Fetch transactions
    expenses = Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_time).all()
    incomes = Income.query.filter(Income.user_id == user_id, Income.date >= start_time).all()

    if not expenses and not incomes:
        return {"message": f"No transactions found for {timeframe}."}

    # ✅ Compute total income & spending
    total_spent = sum(exp.amount for exp in expenses)
    total_earned = sum(inc.amount for inc in incomes)

    # ✅ Find top spending category
    category_spend = {}
    for exp in expenses:
        category_spend[exp.category] = category_spend.get(exp.category, 0) + exp.amount

    top_category = max(category_spend, key=category_spend.get) if category_spend else "No category"

    # ✅ Predict Future Spending
    prev_month_expenses = Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_time - timedelta(days=30)).all()
    prev_month_spent = sum(exp.amount for exp in prev_month_expenses)

    growth_rate = ((total_spent - prev_month_spent) / prev_month_spent) if prev_month_spent > 0 else 0.05
    predicted_next_month_spending = round(total_spent * (1 + growth_rate), 2)

    # ✅ Detect Kiswahili
    is_kiswahili = detect_language(user_prompt)

    # ✅ AI Prompt for Chat or Financial Insights
    if user_prompt:
        prompt = f"User asked: {user_prompt}. Their income: KSH {total_earned}, expenses: KSH {total_spent}, top category: {top_category}."
    else:
        prompt = (
            f"My financial summary for {timeframe}: Spent KSH {total_spent}, earned KSH {total_earned}. "
            f"Top category: {top_category}. Predict my next month's spending and provide budgeting tips."
        )

    # ✅ Call Hugging Face AI API
    response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        return {"message": "AI service unavailable"}

    ai_response = response.json()[0]["generated_text"]
    ai_response = " ".join(ai_response.split())  # Clean whitespace

    # ✅ Data for Graphs (Historical & Predicted Trends)
    trend_data = [
        {"name": "Last Month", "spending": prev_month_spent, "savings": total_earned - prev_month_spent},
        {"name": "This Month", "spending": total_spent, "savings": total_earned - total_spent},
        {"name": "Next Month (Predicted)", "spending": predicted_next_month_spending, "savings": total_earned - predicted_next_month_spending}
    ]

    return {
        "total_spent": total_spent,
        "total_earned": total_earned,
        "top_category": top_category,
        "predicted_next_month_spending": predicted_next_month_spending,
        "ai_insights": ai_response,
        "trend_data": trend_data
    }
