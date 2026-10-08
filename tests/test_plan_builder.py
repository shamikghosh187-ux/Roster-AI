from roster.plan_builder import build

def test_plan_builder_creates_executable_goal_step(): assert build("backup files").ids()==("goal",)
