import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "lms_workers",
    broker=redis_url,
    backend=redis_url,
    include=["workers.tasks"]
)

# Load additional worker settings
celery_app.config_from_object("workers.worker_config")

if __name__ == "__main__":
    celery_app.start()
