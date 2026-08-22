"""Celery tasks for migration."""
from api_guardian.workers.celery_app import app

@app.task
def generate_migration_task(campaign_id: str):
    pass
