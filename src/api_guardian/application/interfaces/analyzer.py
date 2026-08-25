"""Language analysis adapters."""

from typing import Protocol

from api_guardian.analysis.models import Module


class LanguageAdapter(Protocol):
    """Clean parser abstraction for producing Common Code Models."""

    def analyze_file(self, file_path: str, source_code: str) -> Module:
        """Parses the file and returns the common intermediate representation."""
        ...
