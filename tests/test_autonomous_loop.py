from roster.autonomous_loop import AutonomousObservationLoop


def test_loop_observes_before_and_after_and_stops_on_verified_state():
    events = []
    loop = AutonomousObservationLoop(max_cycles=3)
    state = {"value": 0}

    def observe():
        events.append("observe")
        return dict(state)

    def decide(current, history):
        if current["value"] >= 1:
            return None
        return "increment"

    def act(decision):
        events.append(decision)
        state["value"] += 1
        return "changed"

    def verify(decision, after):
        return after["value"] == 1

    result = loop.run(observe=observe, decide=decide, act=act, verify=verify)
    assert result.status == "verified"
    assert result.cycles == 1
    assert events == ["observe", "increment", "observe"]


def test_loop_is_bounded_when_verification_never_succeeds():
    loop = AutonomousObservationLoop(max_cycles=2)
    calls = {"act": 0}

    def observe():
        return {"stable": False}

    def decide(current, history):
        return "try"

    def act(decision):
        calls["act"] += 1
        return "done"

    result = loop.run(
        observe=observe,
        decide=decide,
        act=act,
        verify=lambda decision, after: False,
    )
    assert result.status == "limit_reached"
    assert result.cycles == 2
    assert calls["act"] == 2


def test_loop_does_not_act_when_decision_is_complete():
    loop = AutonomousObservationLoop(max_cycles=2)
    calls = {"act": 0}
    result = loop.run(
        observe=lambda: {"done": True},
        decide=lambda current, history: None,
        act=lambda decision: calls.__setitem__("act", calls["act"] + 1),
        verify=lambda decision, after: True,
    )
    assert result.status == "complete"
    assert calls["act"] == 0
