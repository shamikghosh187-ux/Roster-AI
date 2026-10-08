"""Trust boundaries for data flowing between cognitive workflow steps.

Provider/tool output is untrusted data. A workflow may use verified output as
input to read-only/data-processing actions, but it may not turn arbitrary
tool output directly into a desktop, messaging, or media-control command.
"""

from __future__ import annotations

from dataclasses import dataclass

from roster.models import Action


@dataclass(frozen=True)
class WorkflowResultReference:
    key: str


class WorkflowTrustBoundaryError(RuntimeError):
    """Raised when workflow data would cross into an unsafe action sink."""


# These actions consume text/data without directly causing an external side
# effect. They are the only sinks allowed to receive $RESULT references.
SAFE_RESULT_CONSUMERS = frozenset(
    {
        Action.CHAT,
        Action.SEARCH,
        Action.LIST_FILES,
        Action.READ_FILE,
        Action.FIND_IN_FILES,
        Action.DESKTOP_STATE,
    }
)


def validate_result_reference(action: Action, reference: WorkflowResultReference) -> None:
    """Reject untrusted result -> side-effecting action flows."""
    if action not in SAFE_RESULT_CONSUMERS:
        raise WorkflowTrustBoundaryError(
            f"workflow result '{reference.key}' cannot be used as an argument "
            f"for side-effecting action '{action.value}'"
        )
