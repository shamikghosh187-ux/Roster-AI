from roster.execution_verifier import ExecutionVerifier
from roster.models import Action, Intent


def test_unknown_verification_is_not_success():
    result = ExecutionVerifier().verify(
        Intent(action=Action.OPEN_APP, argument="notepad"),
        "Opening notepad.",
        goal="open notepad",
    )
    assert result.status == "unknown"
    assert not result.verified
    assert not result.failed


def test_tool_failure_envelope_is_failed():
    result = ExecutionVerifier().verify(
        Intent(action=Action.OPEN_APP, argument="notepad"),
        "The open_app tool failed: access denied",
        goal="open notepad",
    )
    assert result.failed
