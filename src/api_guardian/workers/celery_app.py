"""Celery application configuration."""
import os
from celery import Celery

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "api_guardian",
    broker=redis_url,
    backend=redis_url,
    include=[
        "api_guardian.workers.tasks.analysis",
        "api_guardian.workers.tasks.migration",
        "api_guardian.workers.tasks.verification"
    ]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max
)
