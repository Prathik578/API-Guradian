"""Stripe-specific exception types."""

class StripeRateLimitError(Exception):
    """Raised when a 429 is encountered, with the retry_after value."""
    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after

class StripeSyncError(Exception):
    """Raised for non-transient Stripe synchronization errors."""
