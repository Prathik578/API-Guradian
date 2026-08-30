"""JavaScript and TypeScript Analyzer."""

import re

from api_guardian.analysis.models import (
    CallSite,
    CodeLocation,
    EvidenceLevel,
    Module,
    Symbol,
    SymbolType,
)
from api_guardian.application.interfaces.analyzer import LanguageAdapter


class JSTSAnalyzer(LanguageAdapter):
    """Extracts the Common Code Model from JS/TS source files."""

    def analyze_file(self, file_path: str, source_code: str) -> Module:
        module = Module(path=file_path)
        aliases: dict[str, str] = {}
        
        # 1. Parse imports and requires
        # require('stripe')
        require_pattern = re.compile(r"(?:const|let|var)\s+([\w\d_]+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)")
        for match in require_pattern.finditer(source_code):
            alias, mod_name = match.groups()
            module.imports.append(mod_name)
            aliases[alias] = mod_name

        # require('stripe')('sk_test_...') -> immediately initialized SDKs
        require_init_pattern = re.compile(r"(?:const|let|var)\s+([\w\d_]+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)\([^)]*\)")
        for match in require_init_pattern.finditer(source_code):
            alias, mod_name = match.groups()
            module.imports.append(mod_name)
            aliases[alias] = mod_name

        # import ... from ...
        import_default_pattern = re.compile(r"import\s+([\w\d_]+)\s+from\s+['\"]([^'\"]+)['\"]")
        for match in import_default_pattern.finditer(source_code):
            alias, mod_name = match.groups()
            module.imports.append(mod_name)
            aliases[alias] = mod_name

        import_namespace_pattern = re.compile(r"import\s+\*\s+as\s+([\w\d_]+)\s+from\s+['\"]([^'\"]+)['\"]")
        for match in import_namespace_pattern.finditer(source_code):
            alias, mod_name = match.groups()
            module.imports.append(mod_name)
            aliases[alias] = mod_name

        import_named_pattern = re.compile(r"import\s+\{([^}]+)\}\s+from\s+['\"]([^'\"]+)['\"]")
        for match in import_named_pattern.finditer(source_code):
            named_group, mod_name = match.groups()
            module.imports.append(mod_name)
            for part in named_group.split(","):
                part = part.strip()
                if not part:
                    continue
                if " as " in part:
                    orig, alias = part.split(" as ")
                    aliases[alias.strip()] = f"{mod_name}.{orig.strip()}"
                else:
                    aliases[part] = f"{mod_name}.{part}"

        # Additional step: SDK initializations e.g. const stripe = new Stripe(...)
        # We need to map `stripe` to `Stripe`
        init_pattern = re.compile(r"(?:const|let|var)\s+([\w\d_]+)\s*=\s*(?:new\s+)?([\w\d_]+)\(")
        for match in init_pattern.finditer(source_code):
            alias, class_name = match.groups()
            if class_name in aliases:
                aliases[alias] = aliases[class_name]

        # 2. Extract function scopes and calls
        # We'll just treat the whole file as a single top-level symbol for MVP, 
        # unless we explicitly parse functions. Since TS/JS is highly asynchronous 
        # and has many arrow functions, grouping all calls in one 'file_scope' symbol is reliable.
        file_scope = Symbol(
            name="__file_scope__",
            symbol_type=SymbolType.FUNCTION,
            location=CodeLocation(line_start=1, line_end=source_code.count('\n') + 1),
            call_sites=[]
        )
        module.symbols.append(file_scope)

        # Find calls: obj.method( or func(
        call_pattern = re.compile(r"([\w\d_\.]+)\s*\(")
        for match in call_pattern.finditer(source_code):
            target_name = match.group(1)
            
            # Skip obvious keywords
            if target_name in ("if", "for", "while", "switch", "catch", "function", "require"):
                continue

            # Resolve aliases
            parts = target_name.split('.')
            if parts[0] in aliases:
                parts[0] = aliases[parts[0]]
            
            resolved_name = ".".join(parts)
            
            line_no = source_code[:match.start()].count('\n') + 1
            
            file_scope.call_sites.append(CallSite(
                target_name=resolved_name,
                location=CodeLocation(line_start=line_no, line_end=line_no),
                evidence_level=EvidenceLevel.HEURISTIC
            ))

        return module
