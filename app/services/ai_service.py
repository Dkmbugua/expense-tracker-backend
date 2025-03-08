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

def analyze_spending(user_id, timeframe="monthly", prompt_text=""):
    """Fetch AI-powered financial advice from Hugging Face API, predict next month's spending, and respond in Kiswahili if needed."""

    # ✅ Get time filter based on timeframe
    now = datetime.utcnow()
    if timeframe == "minute":
        start_time = now - timedelta(minutes=60)
    elif timeframe == "daily":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif timeframe == "weekly":
        start_time = now - timedelta(days=7)
    elif timeframe == "monthly":
        start_time = now - timedelta(days=30)
    else:
        return {"message": "Invalid timeframe. Use 'minute', 'daily', 'weekly', or 'monthly'."}

    # ✅ Fetch transactions
    expenses = Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_time).all()
    incomes = Income.query.filter(Income.user_id == user_id, Income.date >= start_time).all()

    if not expenses:
        return {"message": f"No {timeframe} transactions to analyze."}

    # ✅ Convert to Kenyan Shillings (KSH)
    total_spent_ksh = sum(exp.amount for exp in expenses)
    total_earned_ksh = sum(inc.amount for inc in incomes)

    # ✅ Find top spending category
    category_spend = {}
    for exp in expenses:
        category_spend[exp.category] = category_spend.get(exp.category, 0) + exp.amount

    top_category = max(category_spend, key=category_spend.get) if category_spend else "No category"

    # ✅ Predict Next Month’s Spending Using Trend Analysis
    prev_month_expenses = Expense.query.filter(
        Expense.user_id == user_id, Expense.date >= start_time - timedelta(days=30)
    ).all()
    prev_month_spent = sum(exp.amount for exp in prev_month_expenses)

    if prev_month_spent > 0:
        growth_rate = (total_spent_ksh - prev_month_spent) / prev_month_spent
    else:
        growth_rate = 0.05  # Assume 5% growth if no previous data

    predicted_next_month_spending = total_spent_ksh * (1 + growth_rate)

    # ✅ Detect Kiswahili Language in User's Input
    is_kiswahili = detect_language(prompt_text)

    # ✅ Generate AI Prompt for Financial Advice (In English or Kiswahili)
    prompt = (
        f"My total spending in the last {timeframe} is KSH {total_spent_ksh}. "
        f"My top spending category is {top_category}. "
        f"My total income is KSH {total_earned_ksh}. "
        f"Predict my spending for next month and provide financial advice specific to a Kenyan student. "
        "Include budgeting strategies, transport cost savings, and realistic side hustles for students such as freelance work, online tutoring, or local business ideas."
    )

    # ✅ If Kiswahili detected, modify AI prompt
    if is_kiswahili:
        prompt = (
            f"Gharama zangu kwa wiki iliyopita ni KSH {total_spent_ksh}. "
            f"Kategoria yangu ya matumizi makubwa ni {top_category}. "
            f"Mapato yangu ni KSH {total_earned_ksh}. "
            "Tafadhali tabiri matumizi yangu kwa mwezi ujao na unipe ushauri wa kifedha maalum kwa mwanafunzi wa Kenya. "
            "Niwekee mikakati ya bajeti, jinsi ya kupunguza gharama za usafiri, na kazi za kufanya upande kama vile uandishi wa mtandaoni, kufundisha wanafunzi wengine, au biashara ndogo ndogo."
        )

    # ✅ Send request to Hugging Face API
    response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        return {"message": "AI service unavailable"}

    ai_response = response.json()[0]["generated_text"]

    # ✅ Clean AI response for better readability
    ai_response = ai_response.replace("\n", " ")  # Remove unnecessary newlines
    ai_response = " ".join(ai_response.split())  # Remove extra spaces

    return {
        "total_spent_ksh": total_spent_ksh,
        "total_earned_ksh": total_earned_ksh,
        "top_category": top_category,
        "predicted_next_month_spending": round(predicted_next_month_spending, 2),
        "ai_insights": ai_response
    }
