import anthropic

from roster.config import settings
from roster.providers.base import Provider, SYSTEM_PROMPT, TOOL_HINT, parse_intent


class ClaudeProvider(Provider):
    name = "claude"

    def __init__(self):
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured.")
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def _request(self, messages, tool_descriptions=""):
        response = self.client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.provider_max_tokens,
            system=SYSTEM_PROMPT + (
                "\n" + TOOL_HINT.format(tools=tool_descriptions)
                if tool_descriptions else ""
            ),
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in messages
                if m["role"] in {"user", "assistant"}
            ],
        )
        return "".join(
            block.text for block in response.content
            if getattr(block, "type", None) == "text"
        ).strip()

    def plan(self, user_text, history=None, tool_descriptions=""):
        messages = list(history or [])[-12:]
        messages.append({"role": "user", "content": user_text})
        return parse_intent(self._request(messages, tool_descriptions))

    def chat(self, messages):
        return self._request(messages)
