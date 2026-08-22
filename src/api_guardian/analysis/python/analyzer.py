"""Python AST Analyzer."""
import ast

from api_guardian.analysis.models import CallSite, CodeLocation, Module, Symbol, SymbolType


class PythonASTAnalyzer:
    """Extracts the Common Code Model from Python source files."""

    def analyze_file(self, file_path: str, source_code: str) -> Module:
        module = Module(path=file_path)
        
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            # Handle or log syntax errors in unparsable files
            return module

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                module.imports.append(node.module)

            # In MVP, we might only collect top-level functions and classes
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sym = Symbol(
                    name=node.name,
                    symbol_type=SymbolType.FUNCTION,
                    location=CodeLocation(
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno
                    ),
                    call_sites=self._extract_calls(node)
                )
                module.symbols.append(sym)
            elif isinstance(node, ast.ClassDef):
                sym = Symbol(
                    name=node.name,
                    symbol_type=SymbolType.CLASS,
                    location=CodeLocation(
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno
                    )
                )
                module.symbols.append(sym)

        return module

    def _extract_calls(self, node: ast.AST) -> list[CallSite]:
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    target_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    target_name = child.func.attr
                else:
                    continue

                calls.append(CallSite(
                    target_name=target_name,
                    location=CodeLocation(
                        line_start=child.lineno,
                        line_end=child.end_lineno or child.lineno
                    )
                ))
        return calls
