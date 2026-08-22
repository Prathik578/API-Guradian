"""Orchestrates LLM calls to generate patches."""
import uuid

from api_guardian.analysis.models import DependencyGraph
from api_guardian.application.interfaces.llm import LLMGateway, LLMRole
from api_guardian.reasoning.models import DiffBlock, PatchArtifact
from api_guardian.reasoning.prompt_builder import PromptBuilder


class PatchGenerator:
    """Uses the LLM Gateway to produce candidate PatchArtifacts."""

    def __init__(self, llm_gateway: LLMGateway):
        self.llm = llm_gateway
        self.prompt_builder = PromptBuilder()

    def generate_patch(
        self,
        repository_id: uuid.UUID,
        commit_sha: str,
        provider_name: str,
        change_description: str,
        affected_files: list[str],
        graph: DependencyGraph,
        source_files: dict[str, str]
    ) -> PatchArtifact:
        """Generates a patch artifact using the reasoning model."""
        prompt = self.prompt_builder.build_migration_prompt(
            provider_name, change_description, affected_files, graph, source_files
        )
        
        response_text, _, _ = self.llm.generate_completion(
            role=LLMRole.MIGRATION_REASONING,
            prompt_envelope=prompt,
            max_tokens=4096
        )
        
        diff_blocks = self._parse_diffs(response_text)
        
        return PatchArtifact(
            id=uuid.uuid4(),
            repository_id=repository_id,
            commit_sha=commit_sha,
            diff_blocks=diff_blocks,
            explanation=response_text
        )

    def _parse_diffs(self, response_text: str) -> list[DiffBlock]:
        """Parses unified diff blocks from the raw LLM string."""
        # TODO: Implement robust diff parsing (e.g. searching for ```diff markers)
        # For MVP, returning empty or mocked blocks
        return []
