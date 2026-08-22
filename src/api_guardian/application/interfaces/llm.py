"""LLM Gateway interface (Port)."""
from abc import ABC, abstractmethod
from enum import Enum


class LLMRole(str, Enum):
    SEMANTIC_ANALYSIS = "semantic_analysis_model"
    MIGRATION_REASONING = "migration_reasoning_model"
    PATCH_REVIEW = "patch_review_model"
    FAILURE_DIAGNOSIS = "failure_diagnosis_model"


class LLMGateway(ABC):
    @abstractmethod
    def generate_completion(
        self,
        role: LLMRole,
        prompt_envelope: str,
        max_tokens: int | None = None
    ) -> tuple[str, int, int]:
        """Generates a text completion based on role policy.
        
        Returns:
            Tuple of (response_text, prompt_tokens, completion_tokens).
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        role: LLMRole,
        prompt_envelope: str,
        schema_cls: type,
        max_tokens: int | None = None
    ) -> tuple[dict, int, int]:
        """Generates a structured JSON completion matching schema_cls.
        
        Returns:
            Tuple of (parsed_dict, prompt_tokens, completion_tokens).
        """
        pass
