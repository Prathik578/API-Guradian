"""Constructs context-rich LLM prompts."""
from api_guardian.analysis.models import DependencyGraph


class PromptBuilder:
    """Assembles prompt envelopes with dependency context."""

    def build_migration_prompt(
        self,
        provider_name: str,
        change_description: str,
        affected_files: list[str],
        graph: DependencyGraph,
        source_files: dict[str, str]
    ) -> str:
        """Constructs the prompt instructing the LLM to migrate the code."""
        prompt = (
            f"Provider '{provider_name}' has made the following API change:\n"
            f"```\n{change_description}\n```\n\n"
            "The following files in our repository depend on this API and must be updated:\n"
        )
        
        for file in affected_files:
            prompt += f"\n--- {file} ---\n"
            prompt += f"```python\n{source_files.get(file, '')}\n```\n"
            
        prompt += (
            "\nPlease provide a unified diff to update the code to the new API. "
            "Ensure you maintain the exact same functionality, but swap the API usage."
        )
        return prompt
