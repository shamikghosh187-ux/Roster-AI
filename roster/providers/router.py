from roster.cancel import CancelledError


class ProviderRouter:
    def __init__(self, providers):
        self.providers = list(providers)
        if not self.providers:
            raise ValueError("at least one provider is required")

    @staticmethod
    def _name(provider):
        return getattr(provider, "name", provider.__class__.__name__)

    @property
    def names(self):
        return tuple(self._name(provider) for provider in self.providers)

    def call(self, method, *args, **kwargs):
        errors = []
        for provider in self.providers:
            try:
                return getattr(provider, method)(*args, **kwargs)
            except CancelledError:
                raise
            except Exception as exc:
                errors.append(
                    f"{self._name(provider)}: {type(exc).__name__}: {exc}"
                )
        raise RuntimeError("all providers failed: " + " | ".join(errors))

    def plan(self, *args, **kwargs):
        return self.call("plan", *args, **kwargs)

    def chat(self, *args, **kwargs):
        return self.call("chat", *args, **kwargs)

    def transcribe(self, *args, **kwargs):
        return self.call("transcribe", *args, **kwargs)

    def vision(self, *args, **kwargs):
        return self.call("vision", *args, **kwargs)
