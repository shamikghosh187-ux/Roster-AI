import json

from groq import Groq

from roster.config import settings
from roster.models import Action, Intent
from roster.providers.base import (
    Provider,
    WORKFLOW_PROMPT,
    build_messages,
    parse_intent,
    parse_workflow,
)


class GroqProvider(Provider):
    name = "groq"

    def __init__(self):
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")
        self.client = Groq(api_key=settings.groq_api_key)

    def transcribe(self, audio_path):
        with open(audio_path, "rb") as audio:
            result = self.client.audio.transcriptions.create(
                file=(audio_path, audio.read()),
                model=settings.whisper_model,
                response_format="text",
            )
        return str(result).strip()

    def plan(self, user_text, history=None, tool_descriptions=""):
        messages = build_messages(user_text, history, tool_descriptions)
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            temperature=0.2,
            messages=messages,
        )
        return parse_intent(response.choices[0].message.content)

    def workflow_plan(self, user_text, history=None, tool_descriptions=""):
        messages = [
            {"role": "system", "content": WORKFLOW_PROMPT},
            {"role": "system", "content": f"Available tools:\n{tool_descriptions}"},
        ]
        if history:
            messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_text})
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            temperature=0.1,
            messages=messages,
            response_format={"type": "json_object"},
        )
        return parse_workflow(response.choices[0].message.content)

    def chat(self, messages):
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            temperature=0.2,
            messages=messages,
        )
        return (response.choices[0].message.content or "").strip()

    def vision(self, user_text, image_data_url):
        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"User request: {user_text}\nAnalyze the screenshot and give concise, useful help.",
                    },
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }],
        )
        return (response.choices[0].message.content or "").strip()
