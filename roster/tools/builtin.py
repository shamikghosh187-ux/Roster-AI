import base64
import os
import subprocess
import tempfile
import urllib.parse
import webbrowser
import pyautogui
import pywhatkit
from roster.models import Action

class ToolExecutor:
    def execute(self, intent, user_text, vision_provider=None):
        if intent.action is Action.EXIT:
            return False, "Goodbye!"
        if intent.action is Action.CHAT:
            return True, intent.argument
        if intent.action is Action.OPEN_APP:
            return True, self.open_app(intent.argument)
        if intent.action is Action.SEARCH:
            return True, self.search(intent.argument)
        if intent.action is Action.YOUTUBE:
            return True, self.youtube(intent.argument)
        if intent.action is Action.WHATSAPP:
            return True, self.whatsapp(intent.argument)
        if intent.action is Action.SCREEN_VISION:
            return True, self.screen_vision(user_text, vision_provider) if vision_provider else "Screen vision is unavailable."
        return True, "I couldn't determine the requested action."

    @staticmethod
    def open_app(name):
        if not name:
            return "Which app should I open?"
        subprocess.Popen(["cmd", "/c", "start", "", name], shell=False)
        return f"Opening {name}."

    @staticmethod
    def search(query):
        if not query:
            return "What should I search for?"
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
        return f"Searching for {query}."

    @staticmethod
    def youtube(query):
        if not query:
            return "What should I play?"
        pywhatkit.playonyt(query)
        return f"Playing {query}."

    @staticmethod
    def whatsapp(argument):
        if "," not in argument:
            return "Please provide the phone number and message."
        phone, message = (x.strip() for x in argument.split(",", 1))
        if not phone or not message:
            return "I need both the phone number and message."
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=3)
        return "WhatsApp message sent."

    @staticmethod
    def screen_vision(user_text, provider):
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
