import os
import random
import spacy
import base64
import io
import matplotlib.pyplot as plt
from flask import jsonify
from models.expenses import Expense
from models.income import Income
from models.user import User
from datetime import datetime, timedelta
import pickle

# Load Trained Chatbot Model
nlp = spacy.load("chatbot_model")

# Load Response Mapping
with open("responses.pkl", "rb") as file:
    responses = pickle.load(file)

# Enhanced Training Data for Kenyan Finance & Students
training_data = [
    {"tag": "savings", "patterns": [
        "How can I save money?", "Give me saving tips.", "Best way to save?",
        "What percentage of income should I save?", "How do I save for a goal?",
        "Give me a personal finance plan.", "How do I save on a low income?",
        "How can a student save money?", "What are the best Kenyan savings accounts?"
    ], "responses": [
        "Use the 50/30/20 rule.", "Track your expenses daily.", "Avoid unnecessary spending.",
        "Automate your savings.", "Set specific savings goals.", "Cut unnecessary costs.",
        "Consider opening a M-Shwari savings account.", "Save part of your HELB loan for emergencies."
    ]},
    {"tag": "budgeting", "patterns": [
        "How do I create a budget?", "Give me budgeting advice.", "Best way to manage expenses?",
        "What is the best budgeting strategy?", "How can I stick to my budget?",
        "Help me make a budget plan.", "How do I budget unexpected expenses?",
        "How can a student budget their money?", "How do I manage my HELB loan?"
    ], "responses": [
        "List your income & expenses.", "Use a finance tracking app.", "Prioritize essential expenses.",
        "Adjust your budget monthly.", "Allocate money to fixed & variable expenses.",
        "Consider using mobile banking apps like KCB M-Pesa for tracking."
    ]},
    {"tag": "investments", "patterns": [
        "Where should I invest?", "Best investments in Kenya?", "How can I grow my money?",
        "Is crypto a good investment?", "What are safe investment options?",
        "Give me long-term investment advice.", "How do I invest in stocks?",
        "Are SACCOs a good investment in Kenya?", "How do I start investing as a student?"
    ], "responses": [
        "Invest in government bonds.", "Join a SACCO.", "Consider real estate.",
        "Diversify your investment portfolio.", "Start with index funds.",
        "SACCOs are a safe and regulated way to invest.", "Try mutual funds through apps like Absa Wealth."
    ]},
    {"tag": "loans", "patterns": [
        "Should I take a loan?", "How do loans work?", "Best way to pay off a loan?",
        "What is a good interest rate?", "Is it bad to have multiple loans?",
        "Should I consolidate my debt?", "How do I reduce loan interest?",
        "Should students take HELB loans?", "What are the best bank loans in Kenya?"
    ], "responses": [
        "Only take a loan if necessary.", "Check the interest rates before borrowing.", "Pay off high-interest loans first.",
        "Avoid payday loans.", "Make more than the minimum payments.",
        "HELB loans are useful but should be spent wisely.", "Compare loan interest rates from banks like KCB, Equity, and Co-op."
    ]}
]

# Enhance chatbot with new training data
def train_chatbot():
    nlp.initialize()
    for _ in range(15):  # Train for 15 iterations
        losses = {}
        for data in training_data:
            for pattern in data["patterns"]:
                doc = nlp.make_doc(pattern)
                example = spacy.training.Example.from_dict(doc, {"cats": {data["tag"]: 1.0}})
                nlp.update([example], losses=losses)

    # Save trained model
    nlp.to_disk("chatbot_model")
    with open("responses.pkl", "wb") as file:
        pickle.dump(training_data, file)
    print("✅ AI Model Trained & Saved as 'chatbot_model'")

# Financial Analysis Function
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

    # Generate Expense Breakdown Chart
    img = io.BytesIO()
    plt.figure(figsize=(8, 4))
    plt.pie(category_spend.values(), labels=category_spend.keys(), autopct='%1.1f%%', startangle=140, colors=["#FF9999", "#66B3FF", "#99FF99", "#FFCC99"])
    plt.title("Expense Breakdown (KSH)")
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    encoded_img = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    # Generate AI Financial Advice
    advice = chatbot_response(f"Advice for {user_name} with savings {savings}")

    return {
        "greeting": f"Hello {user_name} 👋, here's your financial breakdown:",
        "total_income": total_earned,
        "total_expenses": total_spent,
        "savings": savings,
        "top_category": top_category,
        "advice": advice,
        "chart": f"data:image/png;base64,{encoded_img}"  # Embed the chart directly
    }

def chatbot_response(user_input):
    doc = nlp(user_input)
    predicted_intent = max(doc.cats, key=doc.cats.get)
    for intent in training_data:
        if intent["tag"] == predicted_intent:
            return random.choice(intent["responses"])
    return "I don't have an answer for that."
