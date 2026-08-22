"""Routes initialization."""
from . import health
from . import webhooks
from . import cases

__all__ = ["health", "webhooks", "cases"]
