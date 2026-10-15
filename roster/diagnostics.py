"""Dependency diagnostics that remain safe when optional SDKs are absent."""
import importlib.util


class Diagnostics:
    # Keep this list aligned with requirements.txt. Dotted module names are
    # checked defensively because find_spec("parent.child") raises when parent
    # is not installed.
    REQUIRED_MODULES = (
        "groq",
        "anthropic",
        "openai",
        "google.genai",
        "sounddevice",
        "pyttsx3",
        "numpy",
        "scipy",
        "pyautogui",
        "pywhatkit",
    )

    @staticmethod
    def _available(name):
        try:
            return importlib.util.find_spec(name) is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def check(self, names):
        return [{"name": name, "ok": self._available(name)} for name in names]

    def report(self):
        return {"runtime": "python", "checks": self.check(self.REQUIRED_MODULES)}
