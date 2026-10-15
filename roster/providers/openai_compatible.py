"""OpenAI-compatible adapters for additional hosted model providers.

These adapters deliberately implement text planning/chat/workflow planning only.
Speech transcription and vision remain capability-specific and are not claimed here.
"""
import json
import os

from openai import OpenAI

from roster.providers.base import (
    Provider,
    WORKFLOW_PROMPT,
    build_messages,
    parse_intent,
    parse_workflow,
)


class OpenAICompatibleProvider(Provider):
    """Small shared adapter for providers exposing an OpenAI-compatible API."""

    name = "openai-compatible"
    api_key_env = ""
    base_url = ""
    default_model = ""

    def __init__(self):
        api_key = os.getenv(self.api_key_env, "").strip()
        if not api_key:
            raise RuntimeError(f"{self.api_key_env} is not configured.")
        self.model = os.getenv(f"ROSTER_{self.name.upper()}_MODEL", self.default_model).strip()
        if not self.model:
            raise RuntimeError(f"Model is empty for provider {self.name}.")
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)

    def _complete(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return (response.choices[0].message.content or "").strip()

    def plan(self, user_text, history=None, tool_descriptions=""):
        return parse_intent(
            self._complete(build_messages(user_text, history, tool_descriptions))
        )

    def workflow_plan(self, user_text, history=None, tool_descriptions=""):
        messages = [
            {"role": "system", "content": WORKFLOW_PROMPT},
            {"role": "system", "content": f"Available tools:\\n{tool_descriptions}"},
        ]
        if history:
            messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_text})
        raw = self._complete(messages)
        # Some compatible endpoints wrap JSON in Markdown fences despite the
        # instruction; remove only a simple surrounding fence before parsing.
        if raw.startswith("```"):
            raw = raw.split("\\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3].strip()
        return parse_workflow(raw)

    def chat(self, messages):
        return self._complete(messages)


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    api_key_env = "OPENROUTER_API_KEY"
    base_url = "https://openrouter.ai/api/v1"
    default_model = "openai/gpt-4o-mini"


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"
    api_key_env = "DEEPSEEK_API_KEY"
    base_url = "https://api.deepseek.com"
    default_model = "deepseek-chat"


class MistralProvider(OpenAICompatibleProvider):
    name = "mistral"
    api_key_env = "MISTRAL_API_KEY"
    base_url = "https://api.mistral.ai/v1"
    default_model = "mistral-large-latest"


class TogetherProvider(OpenAICompatibleProvider):
    name = "together"
    api_key_env = "TOGETHER_API_KEY"
    base_url = "https://api.together.xyz/v1"
    default_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


class FireworksProvider(OpenAICompatibleProvider):
    name = "fireworks"
    api_key_env = "FIREWORKS_API_KEY"
    base_url = "https://api.fireworks.ai/inference/v1"
    default_model = "accounts/fireworks/models/llama-v3p3-70b-instruct"


class CerebrasProvider(OpenAICompatibleProvider):
    name = "cerebras"
    api_key_env = "CEREBRAS_API_KEY"
    base_url = "https://api.cerebras.ai/v1"
    default_model = "gpt-oss-120b"


class SambaNovaProvider(OpenAICompatibleProvider):
    name = "sambanova"
    api_key_env = "SAMBANOVA_API_KEY"
    base_url = "https://api.sambanova.ai/v1"
    default_model = "Meta-Llama-3.3-70B-Instruct"


class PerplexityProvider(OpenAICompatibleProvider):
    name = "perplexity"
    api_key_env = "PERPLEXITY_API_KEY"
    base_url = "https://api.perplexity.ai"
    default_model = "sonar"


class NvidiaProvider(OpenAICompatibleProvider):
    name = "nvidia"
    api_key_env = "NVIDIA_API_KEY"
    base_url = "https://integrate.api.nvidia.com/v1"
    default_model = "meta/llama-3.3-70b-instruct"
