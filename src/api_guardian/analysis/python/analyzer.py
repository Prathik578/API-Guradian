"""Python AST Analyzer."""

import ast

from api_guardian.analysis.models import CallSite, CodeLocation, Module, Symbol, SymbolType


class PythonASTAnalyzer:
    """Extracts the Common Code Model from Python source files."""

    def analyze_file(self, file_path: str, source_code: str) -> Module:
        module = Module(path=file_path)
        aliases = {}

        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            return module

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module.imports.append(alias.name)
                    aliases[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                module.imports.append(node.module)
                for alias in node.names:
                    aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"

            # In MVP, we might only collect top-level functions and classes
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sym = Symbol(
                    name=node.name,
                    symbol_type=SymbolType.FUNCTION,
                    location=CodeLocation(
                        line_start=node.lineno, line_end=node.end_lineno or node.lineno
                    ),
                    call_sites=self._extract_calls(node, aliases),
                )
                module.symbols.append(sym)
            elif isinstance(node, ast.ClassDef):
                sym = Symbol(
                    name=node.name,
                    symbol_type=SymbolType.CLASS,
                    location=CodeLocation(
                        line_start=node.lineno, line_end=node.end_lineno or node.lineno
                    ),
                )
                module.symbols.append(sym)

        return module

    def _extract_calls(self, node: ast.AST, aliases: dict[str, str]) -> list[CallSite]:
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                target_name = self._get_full_name(child.func)
                if not target_name:
                    continue
                
                # Try to map first component using import aliases
                parts = target_name.split('.')
                if parts[0] in aliases:
                    parts[0] = aliases[parts[0]]
                resolved_name = ".".join(parts)

                calls.append(
                    CallSite(
                        target_name=resolved_name,
                        location=CodeLocation(
                            line_start=child.lineno, line_end=child.end_lineno or child.lineno
                        ),
                    )
                )
        return calls

    def _get_full_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._get_full_name(node.value)
            if base:
                return f"{base}.{node.attr}"
            return node.attr
        return None
