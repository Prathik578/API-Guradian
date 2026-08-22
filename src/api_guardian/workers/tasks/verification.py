"""Celery tasks for verification."""
from api_guardian.workers.celery_app import app

@app.task
def execute_verification_task(run_id: str):
    pass
