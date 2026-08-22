"""Aggregates code models into a project-level Dependency Graph."""
import os

from api_guardian.analysis.javascript.analyzer import JSTSAnalyzer
from api_guardian.analysis.models import DependencyGraph
from api_guardian.analysis.python.analyzer import PythonASTAnalyzer


class GraphBuilder:
    def __init__(self) -> None:
        self.py_analyzer = PythonASTAnalyzer()
        self.js_analyzer = JSTSAnalyzer()

    def build_graph(
        self, repository_id: str, commit_sha: str, workspace_path: str
    ) -> DependencyGraph:
        """Walks the workspace and builds the dependency graph."""
        graph = DependencyGraph(repository_id=repository_id, commit_sha=commit_sha)

        for root, _, files in os.walk(workspace_path):
            # Skip common hidden/binary directories
            if ".git" in root or "node_modules" in root or ".venv" in root:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, workspace_path)
                
                module = None
                if file.endswith(".py"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        module = self.py_analyzer.analyze_file(rel_path, f.read())
                elif file.endswith((".js", ".ts", ".jsx", ".tsx")):
                    with open(file_path, "r", encoding="utf-8") as f:
                        module = self.js_analyzer.analyze_file(rel_path, f.read())
                
                if module:
                    graph.modules[rel_path] = module

        self._resolve_edges(graph)
        return graph

    def _resolve_edges(self, graph: DependencyGraph) -> None:
        """Maps intra-project and external dependencies to edges."""
        # TODO: Advanced alias tracking and API entity mapping
