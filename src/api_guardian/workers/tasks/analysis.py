"""Celery tasks for analysis."""
from api_guardian.workers.celery_app import app

@app.task
def analyze_repository_task(repository_id: str, commit_sha: str):
    pass
