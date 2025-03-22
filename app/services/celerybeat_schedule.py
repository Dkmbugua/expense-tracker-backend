from celery.schedules import crontab
from app.services.tasks import log_subscription_payment, celery  # 👈 import celery from tasks

# Define recurring Celery Beat jobs
celery.conf.beat_schedule = {
    "check-subscription-payments-every-minute": {
        "task": "app.services.tasks.log_subscription_payment",
        "schedule": crontab(minute="*"),  # 👈 every minute
        "args": (1,),  # 👈 Dummy test subscription ID (change as needed)
    },
}

celery.conf.timezone = 'Africa/Nairobi'
