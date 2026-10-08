from roster.subtask import Subtask

def test_subtask_preserves_dependencies(): assert Subtask("b","second",("a",)).depends_on==("a",)
