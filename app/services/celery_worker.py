# celery_worker.py

from app import app # ✅ This must be the actual Flask app instance
from app.services.celery_config import celery, init_celery
import app.services.tasks  # ✅ Ensures all tasks are registered

init_celery(app)

# ✅ Expose Celery app instance for CLI to detect
celery_app = celery
