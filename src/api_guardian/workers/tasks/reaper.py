"""Reaper tasks for stalled cases and attempts."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from celery import shared_task
from sqlalchemy import select

from api_guardian.domain.maintenance import MaintenanceCaseState
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import MaintenanceCaseModel

logger = logging.getLogger(__name__)


@shared_task  # type: ignore
def reap_stalled_cases_task(*args: Any, **kwargs: Any) -> None:
    """Finds cases stuck in transient states and recovers or fails them."""
    timeout_threshold = datetime.now(UTC) - timedelta(hours=1)
    
    with db_manager.get_session() as session:
        # We sweep across ALL tenants for this administrative task
        stalled_cases = session.scalars(
            select(MaintenanceCaseModel).where(
                MaintenanceCaseModel.state.in_([
                    MaintenanceCaseState.IMPACT_ANALYZING,
                    MaintenanceCaseState.MIGRATING,
                    MaintenanceCaseState.VERIFYING,
                ]),
                MaintenanceCaseModel.updated_at < timeout_threshold
            )
        ).all()
        
        for case in stalled_cases:
            logger.warning(f"Reaping stalled case {case.id} in state {case.state}")
            # If it's been in this state for over an hour, it's effectively dead.
            # In MVP, we transition to CANCELLED to allow manual intervention, 
            # rather than infinite retry loops.
            try:
                case.state = MaintenanceCaseState.CANCELLED
                case.updated_at = datetime.now(UTC)
                session.add(case)
            except Exception as e:
                logger.error(f"Failed to reap case {case.id}: {e}")
        
        session.commit()
