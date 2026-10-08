from roster.goal_state import GoalStateEngine


def test_goal_state_is_satisfied_by_structured_observation():
    engine = GoalStateEngine()
    expected = engine.parse({
        "conditions": {
            "active_window.title": {"contains": "Editor"},
            "logged_in": True,
        }
    })
    result = engine.evaluate(
        expected,
        observation={"active_window": {"title": "Project Editor"}, "logged_in": True},
    )
    assert result.status == "satisfied"


def test_goal_state_distinguishes_unsatisfied_from_unknown():
    engine = GoalStateEngine()
    expected = engine.parse({"conditions": {"status": "ready"}})
    assert engine.evaluate(expected, observation={"status": "failed"}).status == "unsatisfied"
    assert engine.evaluate(expected, observation={}).status == "unknown"


def test_goal_state_can_verify_tool_result():
    engine = GoalStateEngine()
    expected = engine.parse({"conditions": {"result": {"contains": "created"}}})
    result = engine.evaluate(expected, result="file created successfully")
    assert result.satisfied


def test_goal_state_rejects_empty_or_non_object_state():
    engine = GoalStateEngine()
    for value in ({}, [], "ready"):
        try:
            engine.parse(value)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid expected state was accepted")
