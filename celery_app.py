# celery_app.py
from celery import Celery

# If Redis runs locally on default port:
REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "audio_dft_pipeline",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)