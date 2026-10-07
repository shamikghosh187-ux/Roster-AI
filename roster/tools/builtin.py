import base64
import os
import subprocess
import tempfile
import urllib.parse
import webbrowser

import pyautogui
import pywhatkit

from roster.models import Action, Intent
from roster.tools.registry import ToolRegistry, ToolSpec

class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry()
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        self.registry.register(ToolSpec(Action.EXIT, "End the Roster session.", self._exit))
        self.registry.register(ToolSpec(Action.CHAT, "Answer conversational questions without taking an external action.", self._chat))
        self.registry.register(ToolSpec(Action.OPEN_APP, "Open a Windows application explicitly requested by the user.", self._open_app, True))
        self.registry.register(ToolSpec(Action.SEARCH, "Open a Google search for the requested query.", self._search))
        self.registry.register(ToolSpec(Action.YOUTUBE, "Play the requested media on YouTube.", self._youtube))
        self.registry.register(ToolSpec(Action.WHATSAPP, "Send an explicit WhatsApp message.", self._whatsapp, True))
        self.registry.register(ToolSpec(Action.SCREEN_VISION, "Capture and analyze the current screen.", self._screen_vision))

    def execute(self, intent: Intent, user_text: str, vision_provider=None):
        spec = self.registry.get(intent.action)
        if not spec:
            return True, "I couldn't determine the requested action."
        try:
            result = spec.handler(intent, user_text, vision_provider)
            return intent.action is not Action.EXIT, result
        except Exception as exc:
            return True, f"The {intent.action.value} tool failed: {exc}"

    def _exit(self, intent, user_text, provider):
        return "Goodbye!"

    def _chat(self, intent, user_text, provider):
        return intent.argument or "I’m here."

    @staticmethod
    def _open_app(intent, user_text, provider):
        name = intent.argument
        if not name:
            return "Which app should I open?"
        subprocess.Popen(["cmd", "/c", "start", "", name], shell=False)
        return f"Opening {name}."

    @staticmethod
    def _search(intent, user_text, provider):
        query = intent.argument
        if not query:
            return "What should I search for?"
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
        return f"Searching for {query}."

    @staticmethod
    def _youtube(intent, user_text, provider):
        query = intent.argument
        if not query:
            return "What should I play?"
        pywhatkit.playonyt(query)
        return f"Playing {query}."

    @staticmethod
    def _whatsapp(intent, user_text, provider):
        if "," not in intent.argument:
            return "Please provide the phone number and message."
        phone, message = (x.strip() for x in intent.argument.split(",", 1))
        if not phone or not message:
            return "I need both the phone number and message."
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=3)
        return "WhatsApp message sent."

    @staticmethod
    def _screen_vision(intent, user_text, provider):
        if provider is None:
            return "Screen vision is unavailable."
        fd, path = tempfile.mkstemp(suffix=".png", prefix="roster-screen-")
        os.close(fd)
        try:
            pyautogui.screenshot(path)
            with open(path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("ascii")
            return provider.vision(user_text, "data:image/png;base64," + encoded)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
