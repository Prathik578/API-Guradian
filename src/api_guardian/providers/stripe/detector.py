"""Stripe OpenAPI change detection logic."""

import uuid
from typing import Any

from api_guardian.domain import CandidateChange, EvidenceSource


class StripeChangeDetector:
    """Detects differences between two OpenAPI spec dictionaries."""

    def detect_changes(
        self,
        current_spec: dict[str, Any],
        previous_spec: dict[str, Any] | None,
        current_artifact_id: uuid.UUID,
        previous_artifact_id: uuid.UUID | None,
    ) -> list[CandidateChange]:
        if not previous_spec:
            return []  # Baseline establishment, no changes detected

        changes = []
        
        curr_paths = current_spec.get("paths", {})
        prev_paths = previous_spec.get("paths", {})
        
        # Detect endpoint removals and deprecations
        for path, prev_path_item in prev_paths.items():
            curr_path_item = curr_paths.get(path)
            
            if curr_path_item is None:
                # Endpoint removed completely
                changes.append(
                    CandidateChange(
                        id=uuid.uuid4(),
                        raw_artifact_id=current_artifact_id,
                        previous_artifact_id=previous_artifact_id,
                        provider="stripe",
                        change_type="endpoint_removed",
                        target_entity=path,
                        extracted_summary=f"Endpoint {path} was removed.",
                        evidence_source=EvidenceSource.OBSERVED_SCHEMA_CHANGE,
                        evidence={"before": "present", "after": "absent"},
                    )
                )
                continue
                
            # Check for deprecation or method removal within the path
            for method, prev_op in prev_path_item.items():
                if method.startswith("x-"):
                    continue
                curr_op = curr_path_item.get(method)
                
                if curr_op is None:
                    changes.append(
                        CandidateChange(
                            id=uuid.uuid4(),
                            raw_artifact_id=current_artifact_id,
                            previous_artifact_id=previous_artifact_id,
                            provider="stripe",
                            change_type="endpoint_removed",
                            target_entity=f"{method.upper()} {path}",
                            extracted_summary=f"Method {method.upper()} {path} was removed.",
                            evidence_source=EvidenceSource.OBSERVED_SCHEMA_CHANGE,
                            evidence={"before": "present", "after": "absent"},
                        )
                    )
                    continue
                    
                prev_deprecated = prev_op.get("deprecated", False) or prev_op.get("x-stripeDeprecated", False)
                curr_deprecated = curr_op.get("deprecated", False) or curr_op.get("x-stripeDeprecated", False)
                
                if curr_deprecated and not prev_deprecated:
                    changes.append(
                        CandidateChange(
                            id=uuid.uuid4(),
                            raw_artifact_id=current_artifact_id,
                            previous_artifact_id=previous_artifact_id,
                            provider="stripe",
                            change_type="endpoint_deprecated",
                            target_entity=f"{method.upper()} {path}",
                            extracted_summary=f"Endpoint {method.upper()} {path} was deprecated.",
                            evidence_source=EvidenceSource.OBSERVED_SCHEMA_CHANGE,
                            evidence={"before": {"deprecated": False}, "after": {"deprecated": True}},
                        )
                    )
        
        # We also need to check schemas (components/schemas)
        curr_schemas = current_spec.get("components", {}).get("schemas", {})
        prev_schemas = previous_spec.get("components", {}).get("schemas", {})
        
        for schema_name, prev_schema in prev_schemas.items():
            curr_schema = curr_schemas.get(schema_name)
            if not curr_schema:
                # Top level schema removed
                continue
            
            # Field removals/deprecations
            prev_props = prev_schema.get("properties", {})
            curr_props = curr_schema.get("properties", {})
            
            for prop_name, prev_prop in prev_props.items():
                curr_prop = curr_props.get(prop_name)
                
                if curr_prop is None:
                    changes.append(
                        CandidateChange(
                            id=uuid.uuid4(),
                            raw_artifact_id=current_artifact_id,
                            previous_artifact_id=previous_artifact_id,
                            provider="stripe",
                            change_type="field_removed",
                            target_entity=f"{schema_name}.{prop_name}",
                            extracted_summary=f"Field {prop_name} was removed from {schema_name}.",
                            evidence_source=EvidenceSource.OBSERVED_SCHEMA_CHANGE,
                            evidence={"before": "present", "after": "absent"},
                        )
                    )
                else:
                    prev_dep = prev_prop.get("deprecated", False) or prev_prop.get("x-stripeDeprecated", False)
                    curr_dep = curr_prop.get("deprecated", False) or curr_prop.get("x-stripeDeprecated", False)
                    if curr_dep and not prev_dep:
                        changes.append(
                            CandidateChange(
                                id=uuid.uuid4(),
                                raw_artifact_id=current_artifact_id,
                                previous_artifact_id=previous_artifact_id,
                                provider="stripe",
                                change_type="field_deprecated",
                                target_entity=f"{schema_name}.{prop_name}",
                                extracted_summary=f"Field {prop_name} was deprecated in {schema_name}.",
                                evidence_source=EvidenceSource.OBSERVED_SCHEMA_CHANGE,
                                evidence={"before": {"deprecated": False}, "after": {"deprecated": True}},
                            )
                        )
        
        return changes
