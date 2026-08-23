"""Domain specific exceptions.

These exceptions represent business logic errors and invariant violations.
They should be caught and translated into appropriate HTTP responses at the API layer.
"""


class DomainError(Exception):
    """Base exception for all domain-related errors."""


class InvalidStateTransitionError(DomainError):
    """Raised when an invalid state machine transition is attempted."""

    def __init__(self, entity_type: str, current_state: str, target_state: str):
        self.entity_type = entity_type
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            f"Invalid transition for {entity_type}: "
            f"cannot move from {current_state} to {target_state}"
        )


class ResourceNotFoundError(DomainError):
    """Raised when a required domain resource cannot be found."""


class InvariantViolationError(DomainError):
    """Raised when a core business invariant would be violated."""
