from google import genai
from google.genai import types

from roster.config import settings
from roster.providers.base import (
    Provider,
    WORKFLOW_PROMPT,
    build_messages,
    parse_intent,
    parse_workflow,
)


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def _prompt(self, messages):
        return "\n\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )

    def plan(self, user_text, history=None, tool_descriptions=""):
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=self._prompt(build_messages(user_text, history, tool_descriptions)),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema={
                    "type": "OBJECT",
                    "properties": {
                        "action": {"type": "STRING"},
                        "argument": {"type": "STRING"},
                    },
                    "required": ["action", "argument"],
                },
            ),
        )
        return parse_intent(response.text)

    def workflow_plan(self, user_text, history=None, tool_descriptions=""):
        messages = [
            {"role": "system", "content": WORKFLOW_PROMPT},
            {"role": "system", "content": f"Available tools:\n{tool_descriptions}"},
        ]
        if history:
            messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_text})
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=self._prompt(messages),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema={
                    "type": "OBJECT",
                    "properties": {
                        "steps": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "name": {"type": "STRING"},
                                    "action": {"type": "STRING"},
                                    "argument": {"type": "STRING"},
                                    "depends_on": {
                                        "type": "ARRAY",
                                        "items": {"type": "STRING"},
                                    },
                                },
                                "required": ["name", "action", "argument", "depends_on"],
                            },
                        }
                    },
                    "required": ["steps"],
                },
            ),
        )
        return parse_workflow(response.text)

    def chat(self, messages):
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=self._prompt(messages),
        )
        return (response.text or "").strip()
