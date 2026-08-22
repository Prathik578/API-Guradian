"""Platform Integrations (GitHub, etc)."""

from .github_adapter import GitHubAdapter
from .pr_templates import PRTemplateBuilder

__all__ = ["GitHubAdapter", "PRTemplateBuilder"]
