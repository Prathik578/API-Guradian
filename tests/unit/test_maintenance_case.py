"""Unit tests for MaintenanceCase domain model."""
import uuid

import pytest

from api_guardian.domain.exceptions import InvalidStateTransitionError
from api_guardian.domain.maintenance import MaintenanceCase, MaintenanceCaseState


def test_initial_state() -> None:
    case = MaintenanceCase(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        repository_id=uuid.uuid4(),
        provider_change_id=uuid.uuid4(),
        base_revision_sha="12345"
    )
    assert case.state == MaintenanceCaseState.DISCOVERED

def test_valid_transitions() -> None:
    case = MaintenanceCase(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        repository_id=uuid.uuid4(),
        provider_change_id=uuid.uuid4(),
        base_revision_sha="12345"
    )
    
    # DISCOVERED -> IMPACT_ANALYZING
    case.transition_to(MaintenanceCaseState.IMPACT_ANALYZING)
    assert case.state == MaintenanceCaseState.IMPACT_ANALYZING
    
    # IMPACT_ANALYZING -> AFFECTED_ACTION_REQUIRED
    case.transition_to(MaintenanceCaseState.AFFECTED_ACTION_REQUIRED)
    assert case.state == MaintenanceCaseState.AFFECTED_ACTION_REQUIRED
    
    # AFFECTED_ACTION_REQUIRED -> MIGRATING
    case.transition_to(MaintenanceCaseState.MIGRATING)
    assert case.state == MaintenanceCaseState.MIGRATING
    
    # MIGRATING -> VERIFYING
    case.transition_to(MaintenanceCaseState.VERIFYING)
    assert case.state == MaintenanceCaseState.VERIFYING
    
    # VERIFYING -> PR_OPEN
    case.transition_to(MaintenanceCaseState.PR_OPEN)
    assert case.state == MaintenanceCaseState.PR_OPEN
    
    # PR_OPEN -> RESOLVED
    case.transition_to(MaintenanceCaseState.RESOLVED)
    assert case.state == MaintenanceCaseState.RESOLVED

def test_invalid_transition() -> None:
    case = MaintenanceCase(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        repository_id=uuid.uuid4(),
        provider_change_id=uuid.uuid4(),
        base_revision_sha="12345"
    )
    
    # DISCOVERED -> VERIFYING should fail
    with pytest.raises(InvalidStateTransitionError):
        case.transition_to(MaintenanceCaseState.VERIFYING)

def test_terminal_state_lock() -> None:
    case = MaintenanceCase(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        repository_id=uuid.uuid4(),
        provider_change_id=uuid.uuid4(),
        base_revision_sha="12345",
        state=MaintenanceCaseState.RESOLVED
    )
    
    # Cannot transition out of terminal state
    with pytest.raises(InvalidStateTransitionError):
        case.transition_to(MaintenanceCaseState.MIGRATING)
