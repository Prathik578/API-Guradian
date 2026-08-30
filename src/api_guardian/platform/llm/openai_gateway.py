"""OpenAI LLM Gateway implementation."""

import logging
import os
from typing import Any

import openai

from api_guardian.application.interfaces.llm import LLMGateway, LLMRole

logger = logging.getLogger(__name__)


class LLMConfigurationError(Exception):
    """Raised when LLM is not properly configured."""


class OpenAIGateway(LLMGateway):
    """OpenAI implementation of the LLM Gateway."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not set. External LLM credentials are unavailable.")
        
        self.model = model
        self.client = openai.Client(api_key=self.api_key)

    def generate_completion(
        self, role: LLMRole, prompt_envelope: str, max_tokens: int | None = None
    ) -> tuple[str, int, int]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt_envelope}],
            max_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content or ""
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        
        return content, prompt_tokens, completion_tokens

    def generate_structured(
        self, role: LLMRole, prompt_envelope: str, schema_cls: type, max_tokens: int | None = None
    ) -> tuple[dict[str, Any], int, int]:
        # For structured output, we can use instructor or just rely on JSON mode.
        # MVP: simply request JSON response and parse it (simplified).
        import json
        
        system_prompt = f"You are a helpful assistant. Please output valid JSON matching this schema: {schema_cls.__name__}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_envelope}
            ],
            max_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content or "{}"
        parsed_dict = json.loads(content)
        
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        
        return parsed_dict, prompt_tokens, completion_tokens
