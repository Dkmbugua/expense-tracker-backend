from flask import Flask
from datetime import datetime, timedelta
from models.subscription import Subscription
from app.db import db

def send_reminders():
    today = datetime.today().date()
    upcoming_subscriptions = Subscription.query.filter(
        Subscription.next_payment_date <= today + timedelta(days=3)
    ).all()

    for sub in upcoming_subscriptions:
        print(f"Reminder: Your {sub.name} payment of {sub.amount} KSH is due on {sub.next_payment_date.strftime('%Y-%m-%d')}.")

# Run this function in a scheduled job using Celery or Cron
