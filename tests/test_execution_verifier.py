from roster.execution_verifier import ExecutionVerifier
from roster.models import Action, Intent


def test_verifier_marks_tool_failures_failed():
    result = ExecutionVerifier().verify(
        Intent(Action.OPEN_APP, "notepad"),
        "The open_app tool failed: application target could not be resolved safely",
    )
    assert result.failed


def test_verifier_marks_deterministic_results_verified():
    result = ExecutionVerifier().verify(
        Intent(Action.READ_FILE, "notes.txt"),
        "File: notes.txt\nhello",
    )
    assert result.verified


def test_verifier_does_not_claim_unknown_desktop_state_without_vision():
    result = ExecutionVerifier().verify(
        Intent(Action.OPEN_APP, "notepad"),
        "Opening notepad.",
    )
    assert result.status == "unknown"


def test_verifier_exposes_unknown_state_as_boolean():
    result = ExecutionVerifier().verify(
        Intent(Action.OPEN_APP, "notepad"),
        "Opening notepad.",
    )
    assert result.unknown
    assert not result.failed
    assert not result.verified
