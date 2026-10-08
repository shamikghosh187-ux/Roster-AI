from roster.task_model import Task
from roster.task_state import TaskStateStore

def test_state_store_snapshots_mutable_task_metadata():
    metadata={"source":"user"}
    task=Task(name="job",metadata=metadata)
    stored=TaskStateStore().add(task)
    metadata["source"]="changed"
    assert stored.metadata["source"]=="user"
