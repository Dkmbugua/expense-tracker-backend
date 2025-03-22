# app/services/tasks.py

from datetime import datetime, timedelta
from app.db import db
from models.subscription import Subscription
from models.expenses import Expense
from app.services.celery_config import celery
from app import app  # ✅ Import the actual Flask app instance


@celery.task
def log_subscription_payment(subscription_id):
    with app.app_context():  # ✅ Wrap in context
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return

        db.session.add(Expense(
            user_id=subscription.user_id,
            category="Subscription",
            description=subscription.name,
            amount=subscription.amount,
            date=datetime.utcnow(),
        ))

        frequency_map = {
            "monthly": timedelta(days=30),
            "daily": timedelta(days=1),
            "hourly": timedelta(hours=1),
            "minutely": timedelta(minutes=1),
        }

        subscription.next_payment_date = datetime.utcnow() + frequency_map.get(
            subscription.billing_cycle, timedelta(days=30)
        )
        db.session.commit()

        log_subscription_payment.apply_async((subscription.id,), eta=subscription.next_payment_date)


@celery.task
def send_subscription_reminder(subscription_id):
    with app.app_context():  # ✅ Wrap in context
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return

        if subscription.next_payment_date:
            eta = subscription.next_payment_date - timedelta(days=1)
            if eta > datetime.utcnow():
                send_subscription_reminder.apply_async((subscription.id,), eta=eta)


@celery.task
def schedule_subscription_payment(subscription_id, frequency):
    with app.app_context():  # ✅ Wrap in context
        frequency_map = {
            "monthly": timedelta(days=30),
            "daily": timedelta(days=1),
            "hourly": timedelta(hours=1),
            "minutely": timedelta(minutes=1),
        }

        next_payment = datetime.utcnow() + frequency_map.get(frequency, timedelta(days=30))
        log_subscription_payment.apply_async((subscription_id,), eta=next_payment)
        send_subscription_reminder.apply_async((subscription_id,), eta=next_payment - timedelta(days=1))
