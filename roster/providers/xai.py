from openai import OpenAI

from roster.config import settings
from roster.providers.base import Provider, build_messages, parse_intent


class XAIProvider(Provider):
    name = "xai"

    def __init__(self):
        if not settings.xai_api_key:
            raise RuntimeError("XAI_API_KEY is not configured.")
        self.client = OpenAI(
            api_key=settings.xai_api_key,
            base_url="https://api.x.ai/v1",
        )

    def _complete(self, messages):
        response = self.client.chat.completions.create(
            model=settings.xai_model,
            messages=messages,
            temperature=0.2,
        )
        return (response.choices[0].message.content or "").strip()

    def plan(self, user_text, history=None, tool_descriptions=""):
        return parse_intent(
            self._complete(build_messages(user_text, history, tool_descriptions))
        )

    def chat(self, messages):
        return self._complete(messages)
