import base64
import os
import subprocess
import tempfile
import urllib.parse
import webbrowser
from pathlib import Path

from roster.models import Action, Intent
from roster.tools.registry import ToolRegistry, ToolSpec

class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry()
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        self.registry.register(ToolSpec(Action.EXIT, "End the Roster session.", self._exit))
        self.registry.register(ToolSpec(Action.CHAT, "Answer conversational questions.", self._chat))
        self.registry.register(ToolSpec(Action.OPEN_APP, "Open a Windows application.", self._open_app, True))
        self.registry.register(ToolSpec(Action.SEARCH, "Open a Google search.", self._search))
        self.registry.register(ToolSpec(Action.YOUTUBE, "Play media on YouTube.", self._youtube))
        self.registry.register(ToolSpec(Action.WHATSAPP, "Send an explicit WhatsApp message.", self._whatsapp, True))
        self.registry.register(ToolSpec(Action.SCREEN_VISION, "Capture and analyze the screen.", self._screen_vision, True))
        self.registry.register(ToolSpec(Action.LIST_FILES, "List a directory.", self._list_files))
        self.registry.register(ToolSpec(Action.READ_FILE, "Read a text file.", self._read_file))
        self.registry.register(ToolSpec(Action.FIND_IN_FILES, "Search text across files.", self._find_in_files))
        self.registry.register(ToolSpec(Action.COMPUTER, "Perform a controlled desktop action.", self._computer, True)

    def execute(self, intent, user_text, vision_provider=None):
        spec = self.registry.get(intent.action)
        if not spec: return True, "I couldn't determine the requested action."
        try:
            return intent.action is not Action.EXIT, spec.handler(intent, user_text, vision_provider)
        except Exception as exc:
            return True, f"The {intent.action.value} tool failed: {exc}"

    @staticmethod
    def _exit(intent, user_text, provider): return "Goodbye!"
    @staticmethod
    def _chat(intent, user_text, provider): return intent.argument or "I'm here."

    @staticmethod
    def _open_app(intent, user_text, provider):
        if not intent.argument: return "Which app should I open?"
        subprocess.Popen(["cmd", "/c", "start", "", intent.argument], shell=False)
        return f"Opening {intent.argument}."

    @staticmethod
    def _search(intent, user_text, provider):
        if not intent.argument: return "What should I search for?"
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(intent.argument))
        return f"Searching for {intent.argument}."

    @staticmethod
    def _youtube(intent, user_text, provider):
        import pywhatkit
        if not intent.argument: return "What should I play?"
        pywhatkit.playonyt(intent.argument)
        return f"Playing {intent.argument}."

    @staticmethod
    def _whatsapp(intent, user_text, provider):
        import pywhatkit
        if "," not in intent.argument: return "Please provide the phone number and message."
        phone, message = (x.strip() for x in intent.argument.split(",", 1))
        if not phone or not message: return "I need both the phone number and message."
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=3)
        return "WhatsApp message sent."

    @staticmethod
    def _screen_vision(intent, user_text, provider):
        import pyautogui
        if provider is None: return "Screen vision is unavailable."
        fd, path = tempfile.mkstemp(suffix=".png", prefix="roster-screen-"); os.close(fd)
        try:
            pyautogui.screenshot(path)
            with open(path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("ascii")
            return provider.vision(user_text, "data:image/png;base64," + encoded)
        finally:
            try: os.remove(path)
            except OSError: pass

    @staticmethod
    def _safe_path(raw_path):
        path = Path(raw_path or ".").expanduser()
        return path.resolve() if path.is_absolute() else (Path.cwd() / path).resolve()

    def _list_files(self, intent, user_text, provider):
        path = self._safe_path(intent.argument)
        if not path.exists() or not path.is_dir(): return f"Directory not found: {path}"
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:100]
        return "Contents of " + str(path) + ":\n" + "\n".join(("[DIR] " if p.is_dir() else "[FILE] ") + p.name for p in entries)

    def _read_file(self, intent, user_text, provider):
        path = self._safe_path(intent.argument)
        if not path.exists() or not path.is_file(): return f"File not found: {path}"
        if path.stat().st_size > 2_000_000: return "That file is too large for direct text reading."
        try: text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError: return "That file is not UTF-8 text."
        return f"File: {path}\n{text[:20000]}" + ("\n...[truncated]" if len(text) > 20000 else "")

    def _find_in_files(self, intent, user_text, provider):
        if "::" not in intent.argument: return "Use directory::text for file search."
        directory, needle = (x.strip() for x in intent.argument.split("::", 1))
        root = self._safe_path(directory)
        if not root.is_dir() or not needle: return "A valid directory and search text are required."
        matches = []
        for path in root.rglob("*"):
            if len(matches) >= 50: break
            if not path.is_file() or path.stat().st_size > 2_000_000: continue
            try:
                for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if needle.lower() in line.lower(): matches.append(f"{path}:{line_no}: {line.strip()[:300]}")
            except OSError: continue
        return "No matches found." if not matches else "Matches:\n" + "\n".join(matches[:50])

    @staticmethod
    def _computer(intent, user_text, provider):
        import pyautogui
        parts = intent.argument.strip().split(maxsplit=1)
        if len(parts) != 2: return "Use click x,y, type text, or press key."
        operation, value = parts
        if operation == "click":
            x, y = (int(v.strip()) for v in value.split(",", 1)); pyautogui.click(x, y); return f"Clicked at ({x}, {y})."
        if operation == "type":
            pyautogui.write(value, interval=0.01); return "Typed the requested text."
        if operation == "press":
            pyautogui.press(value.strip()); return f"Pressed {value.strip()}."
        return "Supported: click x,y | type text | press key."
