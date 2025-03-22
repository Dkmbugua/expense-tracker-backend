# app/services/celery_config.py
from celery import Celery

celery = Celery(
    "expense_tracker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[]
)

def init_celery(app):
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            # ⛔ Do NOT use 'app' directly — use 'flask_app'
            from app import app as flask_app
            with flask_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
