"""Maintenance Case and Impact Assessment domain models."""
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from api_guardian.domain.exceptions import InvalidStateTransitionError


class MaintenanceCaseState(str, Enum):
    DISCOVERED = "discovered"
    IMPACT_ANALYZING = "impact_analyzing"
    UNAFFECTED = "unaffected"
    AFFECTED_ACTION_REQUIRED = "affected_action_required"
    MIGRATING = "migrating"
    VERIFYING = "verifying"
    PR_OPEN = "pr_open"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    CANCELLED = "cancelled"
    STALE = "stale"
    MANUALLY_RESOLVED = "manually_resolved"
    HUMAN_INTERVENTION_REQUIRED = "human_intervention_required"


class ImpactClassification(str, Enum):
    CONFIRMED_AFFECTED = "confirmed_affected"
    LIKELY_AFFECTED = "likely_affected"
    NOT_AFFECTED = "not_affected"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class EvidenceLevel(str, Enum):
    DIRECT_MATCH = "direct_match"
    ALIAS_MATCH = "alias_match"
    SEMANTIC_INFERENCE = "semantic_inference"
    NONE = "none"


@dataclass
class ImpactAssessment:
    """Evidence-backed determination of whether the repository is affected."""
    id: uuid.UUID
    case_id: uuid.UUID
    snapshot_id: uuid.UUID
    classification: ImpactClassification
    evidence_level: EvidenceLevel
    affected_files: list[str]
    evidence_payload: dict[str, Any]
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class MaintenanceCase:
    """Aggregate root representing an external change affecting a repository."""
    id: uuid.UUID
    organization_id: uuid.UUID
    repository_id: uuid.UUID
    provider_change_id: uuid.UUID
    base_revision_sha: str
    state: MaintenanceCaseState = MaintenanceCaseState.DISCOVERED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def transition_to(self, new_state: MaintenanceCaseState) -> None:
        """Transitions the case to a new state if valid."""
        valid_transitions = {
            MaintenanceCaseState.DISCOVERED: [MaintenanceCaseState.IMPACT_ANALYZING, MaintenanceCaseState.CANCELLED],
            MaintenanceCaseState.IMPACT_ANALYZING: [
                MaintenanceCaseState.UNAFFECTED, 
                MaintenanceCaseState.AFFECTED_ACTION_REQUIRED,
                MaintenanceCaseState.CANCELLED
            ],
            MaintenanceCaseState.AFFECTED_ACTION_REQUIRED: [
                MaintenanceCaseState.MIGRATING,
                MaintenanceCaseState.MANUALLY_RESOLVED,
                MaintenanceCaseState.SUPPRESSED,
                MaintenanceCaseState.CANCELLED
            ],
            MaintenanceCaseState.MIGRATING: [
                MaintenanceCaseState.VERIFYING,
                MaintenanceCaseState.HUMAN_INTERVENTION_REQUIRED,
                MaintenanceCaseState.STALE,
                MaintenanceCaseState.CANCELLED
            ],
            MaintenanceCaseState.VERIFYING: [
                MaintenanceCaseState.PR_OPEN,
                MaintenanceCaseState.AFFECTED_ACTION_REQUIRED, # e.g. on failure -> retry
                MaintenanceCaseState.HUMAN_INTERVENTION_REQUIRED,
                MaintenanceCaseState.STALE,
                MaintenanceCaseState.CANCELLED
            ],
            MaintenanceCaseState.PR_OPEN: [
                MaintenanceCaseState.RESOLVED,
                MaintenanceCaseState.STALE,
                MaintenanceCaseState.CANCELLED
            ],
            MaintenanceCaseState.STALE: [
                MaintenanceCaseState.IMPACT_ANALYZING,
                MaintenanceCaseState.CANCELLED
            ]
        }

        # Terminal states have no valid outward transitions normally except manual interventions
        terminal_states = {
            MaintenanceCaseState.UNAFFECTED,
            MaintenanceCaseState.RESOLVED,
            MaintenanceCaseState.SUPPRESSED,
            MaintenanceCaseState.MANUALLY_RESOLVED,
            MaintenanceCaseState.CANCELLED,
            MaintenanceCaseState.HUMAN_INTERVENTION_REQUIRED
        }

        if self.state in terminal_states and new_state not in [MaintenanceCaseState.IMPACT_ANALYZING, MaintenanceCaseState.DISCOVERED]:
            # Admins might reset, but generally terminal states don't transition
             raise InvalidStateTransitionError("MaintenanceCase", self.state, new_state)

        if self.state not in terminal_states and new_state not in valid_transitions.get(self.state, []):
            raise InvalidStateTransitionError("MaintenanceCase", self.state, new_state)

        self.state = new_state
        self.updated_at = datetime.now(UTC)
