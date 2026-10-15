from openai import OpenAI

from roster.config import settings
from roster.providers.base import (
    Provider,
    WORKFLOW_PROMPT,
    build_messages,
    parse_intent,
    parse_workflow,
)


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

    def workflow_plan(self, user_text, history=None, tool_descriptions=""):
        messages = [
            {"role": "system", "content": WORKFLOW_PROMPT},
            {"role": "system", "content": f"Available tools:\n{tool_descriptions}"},
        ]
        if history:
            messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_text})
        return parse_workflow(self._complete(messages))

    def chat(self, messages):
        return self._complete(messages)
