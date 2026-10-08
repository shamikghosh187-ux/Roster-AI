from roster.goal import Goal

def test_goal_transitions_to_completed():
    goal=Goal("organize files"); assert not goal.completed; goal.complete(); assert goal.completed
