"""Orchestrates LLM calls to generate patches."""

import uuid
from typing import Any

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
        evidence: dict[str, Any],
        source_files: dict[str, str],
    ) -> PatchArtifact:
        """Generates a patch artifact using the reasoning model."""
        prompt = self.prompt_builder.build_migration_prompt(
            provider_name, change_description, affected_files, evidence, source_files
        )

        from api_guardian.domain.quotas import ResourcePolicy
        policy = ResourcePolicy.get_default()

        response_text, _, _ = self.llm.generate_completion(
            role=LLMRole.MIGRATION_REASONING, prompt_envelope=prompt, max_tokens=policy.migration.max_model_tokens
        )

        diff_blocks = self._parse_diffs(response_text)

        return PatchArtifact(
            id=uuid.uuid4(),
            repository_id=repository_id,
            commit_sha=commit_sha,
            diff_blocks=diff_blocks,
            explanation=response_text,
        )

    def _parse_diffs(self, response_text: str) -> list[DiffBlock]:
        """Parses unified diff blocks from the raw LLM string."""
        import re
        
        diffs = []
        blocks = re.findall(r"```(?:diff)?\n(.*?)\n```", response_text, re.DOTALL)
        if not blocks:
            # Fallback if the LLM didn't use markdown code blocks
            blocks = [response_text]
            
        for block in blocks:
            file_diffs = re.split(r"(?=\n?--- )", block)
            for fd in file_diffs:
                fd = fd.strip()
                if not fd.startswith("--- "):
                    continue
                    
                lines = fd.split("\n")
                if len(lines) < 3:
                    continue
                    
                minus_line = lines[0]
                plus_line = lines[1] if len(lines) > 1 and lines[1].startswith("+++ ") else ""
                
                file_path = ""
                if plus_line:
                    file_path = plus_line[4:].strip()
                else:
                    file_path = minus_line[4:].strip()
                    
                # Clean up a/ and b/ prefixes typically used in unified diffs
                if file_path.startswith("a/") or file_path.startswith("b/"):
                    file_path = file_path[2:]
                    
                if not file_path or file_path == "/dev/null":
                    continue
                    
                hunk = "\n".join(lines[2:])
                diffs.append(DiffBlock(
                    file_path=file_path,
                    original_snippet="",
                    modified_snippet=hunk
                ))
                
        return diffs
