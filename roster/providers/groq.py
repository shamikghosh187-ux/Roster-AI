import json
from groq import Groq
from roster.config import settings
from roster.models import Action, Intent

SYSTEM_PROMPT = """You are Roster, a capable Windows personal AI assistant.
Return ONLY valid JSON with keys: action and argument.
Allowed actions: chat, exit, open_app, search, youtube, whatsapp, screen_vision.
Choose the smallest useful next action for the user's goal.
Use open_app only when explicitly asked to launch an application.
Use search for web/search requests, youtube for media, whatsapp for an explicit message request,
and screen_vision when the user asks you to inspect or troubleshoot the screen.
For chat, argument must contain the final answer.
Use conversation history to understand references such as "it", "that", or "again".
Never invent phone numbers.
You operate inside an execution loop. After a tool result, decide whether another tool is required.
If the user's task is complete, use chat and give the final answer.
Do not repeat a tool that already completed the requested work unless the user asked for it again."""

class GroqProvider:
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
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if tool_descriptions:
            messages.append({"role": "system", "content": "Available tools:\n" + tool_descriptions})
        if history:
            messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_text})
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            temperature=0.2,
            messages=messages,
        )
        raw = (response.choices[0].message.content or "").strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"action": "chat", "argument": raw}
        try:
            action = Action(str(data.get("action", "chat")).lower())
        except ValueError:
            action = Action.CHAT
        return Intent(action=action, argument=str(data.get("argument", "")).strip())

    def vision(self, user_text, image_data_url):
        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": f"User request: {user_text}\nAnalyze the screenshot and give concise, useful help."},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ]}],
        )
        return (response.choices[0].message.content or "").strip()
