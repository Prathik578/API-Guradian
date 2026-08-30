from datetime import UTC, datetime
from typing import Any

from celery import current_app
from sqlalchemy.orm import Session

from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import TaskOutboxModel


class OutboxManager:
    @staticmethod
    def schedule_task(session: Session, task_name: str, payload: dict[str, Any]) -> None:
        """Schedules a Celery task by writing it to the outbox in the current transaction."""
        outbox = TaskOutboxModel(
            task_name=task_name,
            payload=payload,
        )
        session.add(outbox)

    @staticmethod
    def dispatch_pending(db_manager: DatabaseManager) -> None:
        """Dispatches all pending outbox messages to Celery and marks them dispatched."""
        from sqlalchemy import select
        with db_manager.get_session() as session:
            stmt = select(TaskOutboxModel).where(TaskOutboxModel.dispatched_at.is_(None)).with_for_update(skip_locked=True)
            pending = session.scalars(stmt).all()
            for record in pending:
                # Dispatch to Celery
                current_app.send_task(record.task_name, kwargs=record.payload)
                # Mark dispatched
                record.dispatched_at = datetime.now(UTC).isoformat()
            session.commit()
