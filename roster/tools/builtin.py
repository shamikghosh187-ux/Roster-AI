import base64
import os
import shutil
import subprocess
import tempfile
import urllib.parse
import webbrowser
from pathlib import Path

from roster.cancel import CancelledError
from roster.computer_control import execute_computer_command, parse_computer_command
from roster.desktop_perception import DesktopPerception
from roster.execution_policy_resolver import ResolvedExecutionPolicy
from roster.models import Action, Intent
from roster.production_tool_executor import ProductionToolExecutor
from roster.registry_adapter import catalog_from_registry
from roster.tool_contract import ToolContract
from roster.tools.registry import ToolRegistry, ToolSpec


class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry()
        self._register_builtin_tools()
        self._production = ProductionToolExecutor(
            catalog_from_registry(self.registry),
            ResolvedExecutionPolicy(),
        )

    def _register_builtin_tools(self):
        self.registry.register(ToolSpec(Action.EXIT, "End the Roster session.", self._exit))
        self.registry.register(ToolSpec(Action.CHAT, "Answer conversational questions.", self._chat, False, True))
        self.registry.register(ToolSpec(Action.OPEN_APP, "Open a Windows application.", self._open_app, True))
        self.registry.register(ToolSpec(Action.SEARCH, "Open a Google search.", self._search, False, True))
        self.registry.register(ToolSpec(Action.YOUTUBE, "Play media on YouTube.", self._youtube, False, False))
        self.registry.register(ToolSpec(Action.WHATSAPP, "Send an explicit WhatsApp message.", self._whatsapp, True))
        self.registry.register(ToolSpec(Action.SCREEN_VISION, "Capture and analyze the screen.", self._screen_vision, True))
        self.registry.register(ToolSpec(Action.LIST_FILES, "List a directory.", self._list_files, False, True))
        self.registry.register(ToolSpec(Action.READ_FILE, "Read a text file.", self._read_file, False, True))
        self.registry.register(ToolSpec(Action.FIND_IN_FILES, "Search text across files.", self._find_in_files, False, True))
        self.registry.register(ToolSpec(Action.COMPUTER, "Control the desktop with allow-listed operations: move x,y; click x,y; double_click x,y; right_click x,y; drag x1,y1 to x2,y2; type text; press key; hotkey key1+key2; scroll amount.", self._computer, True))
        self.registry.register(ToolSpec(Action.DESKTOP_STATE, "Observe the current desktop and return a typed world-model snapshot.", self._desktop_state, True, True))

    def execute(
        self,
        intent,
        user_text,
        vision_provider=None,
        cancellation=None,
        confirmed=False,
    ):
        spec = self.registry.get(intent.action)
        if not spec:
            return True, "I couldn't determine the requested action."
        if cancellation is not None:
            cancellation.raise_if_cancelled()
        try:
            # Keep the production catalog synchronized with the registry so
            # runtime/tool overrides and test doubles are honored.
            self._production.catalog = catalog_from_registry(self.registry)
            # Preserve the registry's dynamic get() contract as well as its
            # static catalog, so runtime overrides remain observable.
            active_spec = self.registry.get(intent.action)
            if active_spec is not None:
                def invoke(args, ctx, spec=active_spec):
                    context = ctx if isinstance(ctx, dict) else {}
                    argument = args.get("argument", context.get("argument", ""))
                    metadata = dict(context.get("metadata", {}))
                    metadata.update({k: v for k, v in args.items() if k != "argument"})
                    runtime_intent = Intent(
                        action=spec.action,
                        argument=argument,
                        metadata=metadata,
                    )
                    return spec.handler(
                        runtime_intent,
                        context.get("raw_input", ""),
                        context.get("tool_context"),
                    )
                self._production.catalog.upsert(
                    ToolContract(
                        name=active_spec.action.value,
                        description=active_spec.description,
                        input_schema={"type": "object"},
                        sensitive=active_spec.requires_confirmation,
                        retry_safe=active_spec.retry_safe,
                        handler=invoke,
                    )
                )
            result = self._production.execute(
                intent.action.value,
                intent.action.value,
                {"argument": intent.argument},
                confirmed=confirmed,
                cancellation=cancellation,
                context={
                    "raw_input": user_text,
                    "tool_context": vision_provider,
                },
            )
            if not result.ok:
                return True, f"The {intent.action.value} tool failed: {result.error}"
            return intent.action is not Action.EXIT, result.value
        except CancelledError:
            raise
        except Exception as exc:
            return True, f"The {intent.action.value} tool failed: {exc}"

    @staticmethod
    def _exit(intent, user_text, provider):
        return "Goodbye!"

    @staticmethod
    def _chat(intent, user_text, provider):
        return intent.argument or "I'm here."

    @staticmethod
    def _open_app(intent, user_text, provider):
        if not intent.argument:
            return "Which app should I open?"
        target = intent.argument.strip()
        executable = shutil.which(target)
        if executable:
            subprocess.Popen([executable], shell=False)
        elif os.name == "nt" and hasattr(os, "startfile"):
            os.startfile(target)
        else:
            raise OSError("application target could not be resolved safely")
        return f"Opening {target}."

    @staticmethod
    def _search(intent, user_text, provider):
        if not intent.argument:
            return "What should I search for?"
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(intent.argument))
        return f"Searching for {intent.argument}."

    @staticmethod
    def _youtube(intent, user_text, provider):
        import pywhatkit
        if not intent.argument:
            return "What should I play?"
        pywhatkit.playonyt(intent.argument)
        return f"Playing {intent.argument}."

    @staticmethod
    def _whatsapp(intent, user_text, provider):
        import pywhatkit
        if "," not in intent.argument:
            return "Please provide the phone number and message."
        phone, message = (x.strip() for x in intent.argument.split(",", 1))
        if not phone or not message:
            return "I need both the phone number and message."
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=3)
        return "WhatsApp message sent."

    @staticmethod
    def _screen_vision(intent, user_text, provider):
        import pyautogui
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

    @staticmethod
    def _safe_path(raw_path):
        path = Path(raw_path or ".").expanduser().resolve()
        configured = os.getenv("ROSTER_ALLOWED_PATHS", "")
        roots = [Path.cwd().resolve()]
        if configured:
            roots.extend(
                Path(item).expanduser().resolve()
                for item in configured.split(os.pathsep)
                if item.strip()
            )
        if not any(path == root or root in path.parents for root in roots):
            raise PermissionError("path is outside Roster allowed roots")
        return path

    def _list_files(self, intent, user_text, provider):
        path = self._safe_path(intent.argument)
        if not path.exists() or not path.is_dir():
            return f"Directory not found: {path}"
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:100]
        return "Contents of " + str(path) + ":\n" + "\n".join(
            ("[DIR] " if p.is_dir() else "[FILE] ") + p.name for p in entries
        )

    def _read_file(self, intent, user_text, provider):
        path = self._safe_path(intent.argument)
        if not path.exists() or not path.is_file():
            return f"File not found: {path}"
        if path.stat().st_size > 2_000_000:
            return "That file is too large for direct text reading."
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "That file is not UTF-8 text."
        return f"File: {path}\n{text[:20000]}" + ("\n...[truncated]" if len(text) > 20000 else "")

    def _find_in_files(self, intent, user_text, provider):
        if "::" not in intent.argument:
            return "Use directory::text for file search."
        directory, needle = (x.strip() for x in intent.argument.split("::", 1))
        root = self._safe_path(directory)
        if not root.is_dir() or not needle:
            return "A valid directory and search text are required."
        matches = []
        for path in root.rglob("*"):
            if len(matches) >= 50:
                break
            try:
                safe_path = self._safe_path(path)
            except (OSError, PermissionError):
                continue
            if not safe_path.is_file() or safe_path.stat().st_size > 2_000_000:
                continue
            try:
                for line_no, line in enumerate(
                    safe_path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
                ):
                    if needle.lower() in line.lower():
                        matches.append(f"{safe_path}:{line_no}: {line.strip()[:300]}")
                        if len(matches) >= 50:
                            break
            except (OSError, PermissionError):
                continue
        return "No matches found." if not matches else "Matches:\n" + "\n".join(matches)

    @staticmethod
    def _desktop_state(intent, user_text, provider):
        state = DesktopPerception(provider).capture(reason=intent.argument or user_text)
        return state.to_dict()

    @staticmethod
    def _computer(intent, user_text, provider):
        command = parse_computer_command(intent.argument)
        return execute_computer_command(command)
