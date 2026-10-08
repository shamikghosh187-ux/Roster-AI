"""Parse structured workflow plans emitted by an AI provider."""
from __future__ import annotations

from roster.cognitive_task_graph import CognitiveTaskGraph, CognitiveTaskSpec


class CognitivePlanningError(ValueError):
    pass


class CognitivePlanner:
    """Converts provider-neutral structured plans into validated task graphs."""

    def from_specs(self, raw_steps):
        if not isinstance(raw_steps, list) or not raw_steps:
            raise CognitivePlanningError("workflow must contain at least one step")

        specs = []
        for index, raw in enumerate(raw_steps, 1):
            if not isinstance(raw, dict):
                raise CognitivePlanningError(f"step {index} must be an object")
            name = str(raw.get("name", "")).strip()
            if not name:
                raise CognitivePlanningError(f"step {index} has no name")
            dependencies = raw.get("depends_on", ())
            if isinstance(dependencies, str):
                dependencies = (dependencies,)
            if not isinstance(dependencies, (list, tuple)):
                raise CognitivePlanningError(f"step {index} dependencies must be a list")

            metadata = dict(raw.get("metadata") or {})
            # Keep the wire format compact: action/argument can live at the
            # step level, while metadata remains available for provider hints.
            if raw.get("action") is not None:
                metadata["action"] = str(raw["action"]).strip().lower()
            if raw.get("argument") is not None:
                metadata["argument"] = str(raw["argument"])

            specs.append(
                CognitiveTaskSpec(
                    name=name,
                    input=str(raw.get("input", raw.get("argument", ""))),
                    depends_on=tuple(str(item) for item in dependencies),
                    priority=int(raw.get("priority", 0)),
                    metadata=metadata,
                )
            )
        return CognitiveTaskGraph(specs)
