"""Stripe change interpretation logic."""

import hashlib
import uuid
from datetime import UTC, datetime

from api_guardian.domain import CandidateChange, ChangeClassification, ProviderChange


class StripeChangeInterpreter:
    """Interprets CandidateChanges into canonical ProviderChanges."""

    def interpret_change(self, candidate: CandidateChange) -> ProviderChange:
        classification = self._classify(candidate.change_type)
        native_id = self.compute_canonical_change_id(candidate.provider, candidate.change_type, candidate.target_entity)

        return ProviderChange(
            id=uuid.uuid4(),
            provider=candidate.provider,
            provider_native_id=native_id,
            classification=classification,
            summary=candidate.extracted_summary,
            affected_entities=[candidate.target_entity],
            effective_date=None,  # Not invented
            sunset_date=None,     # Not invented
            source_artifact_hash=None, # Will be set by the use case
            revision=1,
            created_at=datetime.now(UTC)
        )
        
    def _classify(self, change_type: str) -> ChangeClassification:
        mapping = {
            "endpoint_removed": ChangeClassification.BREAKING_BEHAVIOR,
            "endpoint_deprecated": ChangeClassification.DEPRECATION,
            "field_removed": ChangeClassification.BREAKING_BEHAVIOR,
            "field_deprecated": ChangeClassification.DEPRECATION,
            "parameter_removed": ChangeClassification.SIGNATURE_CHANGE,
            "parameter_added_required": ChangeClassification.SIGNATURE_CHANGE,
            "schema_type_changed": ChangeClassification.BREAKING_BEHAVIOR,
        }
        return mapping.get(change_type, ChangeClassification.UNKNOWN)

    @staticmethod
    def compute_canonical_change_id(provider: str, change_type: str, target_entity: str) -> str:
        """
        Computes a deterministic composite hash since Stripe does not provide native change IDs here.
        """
        payload = f"{provider}:{change_type}:{target_entity}".encode()
        return hashlib.sha256(payload).hexdigest()
