"""Common Code Model for language-neutral representation."""

from dataclasses import dataclass, field
from enum import Enum


class SymbolType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    IMPORT = "import"


class EvidenceLevel(str, Enum):
    DIRECT = "DIRECT"
    ALIAS = "ALIAS"
    WRAPPER = "WRAPPER"
    HEURISTIC = "HEURISTIC"
    UNRESOLVED = "UNRESOLVED"


@dataclass
class CodeLocation:
    line_start: int
    line_end: int
    column_start: int | None = None
    column_end: int | None = None


@dataclass
class CallSite:
    """Represents a location where an API or function is invoked."""

    target_name: str
    location: CodeLocation
    context_snippet: str | None = None
    evidence_level: str = EvidenceLevel.DIRECT


@dataclass
class Symbol:
    """Represents a defined entity (function, class) in the code."""

    name: str
    symbol_type: SymbolType
    location: CodeLocation
    call_sites: list[CallSite] = field(default_factory=list)


@dataclass
class Module:
    """Represents a file or logical module."""

    path: str
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


@dataclass
class DependencyEdge:
    """Represents a dependency relationship (e.g. customer code -> Provider API)."""

    source_file: str
    source_symbol: str
    target_provider: str
    target_entity: str
    call_site: CallSite
    evidence_level: str = EvidenceLevel.DIRECT


@dataclass
class DependencyGraph:
    """Project-level aggregation of dependencies."""

    repository_id: str
    commit_sha: str
    modules: dict[str, Module] = field(default_factory=dict)
    edges: list[DependencyEdge] = field(default_factory=list)
