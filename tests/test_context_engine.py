from roster.context_engine import ContextEngine


def test_world_model_tracks_observations_and_detects_staleness():
    engine = ContextEngine(desktop_max_age=5)
    engine.begin("open the project")
    engine.observe_desktop(
        {
            "timestamp": 100.0,
            "screen_size": (1920, 1080),
            "source": "local",
            "confidence": 0.25,
            "windows": [],
        }
    )
    assert engine.world.goal == "open the project"
    assert engine.world.get("desktop") is not None
    assert engine.desktop_needs_refresh() is True


def test_planning_context_marks_missing_desktop_state_as_unknown():
    engine = ContextEngine()
    engine.begin("find the failing test")
    context = engine.planning_context()
    assert "Desktop observation: unavailable" in context
    assert "do not assume" in context


def test_fresh_desktop_observation_is_available_to_planner():
    engine = ContextEngine(desktop_max_age=60)
    engine.begin("inspect the current app")
    engine.observe_desktop(
        {
            "timestamp": __import__("time").time(),
            "source": "test",
            "confidence": 0.9,
            "windows": [{"title": "Editor"}],
        }
    )
    context = engine.planning_context()
    assert "Desktop state:" in context
    assert "confidence=0.90" in context
    assert "STALE" not in context


def test_recent_actions_are_bounded():
    engine = ContextEngine(max_actions=3)
    engine.begin("test")
    for index in range(20):
        engine.record_action({"step": index})
    assert len(engine.world.recent_actions) == 12
    assert engine.world.recent_actions[-1]["step"] == 19
