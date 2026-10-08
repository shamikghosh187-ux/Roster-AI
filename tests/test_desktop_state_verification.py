from roster.models import Action, Intent
from roster.execution_verifier import ExecutionVerifier


def test_desktop_state_observation_is_verified():
    result = ExecutionVerifier().verify(
        Intent(Action.DESKTOP_STATE, ""),
        {"source": "vision", "confidence": 0.9},
    )
    assert result.verified
