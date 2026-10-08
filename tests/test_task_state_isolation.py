from roster.task_model import Task
from roster.task_state import TaskStateStore

def test_task_state_get_returns_isolated_metadata_snapshot():
    store=TaskStateStore()
    store.add(Task(id="t1",name="job",metadata={"nested":{"owner":"user"}}))
    snapshot=store.get("t1")
    snapshot.metadata["nested"]["owner"]="mutated"
    assert store.get("t1").metadata["nested"]["owner"]=="user"

def test_task_state_all_returns_isolated_snapshots():
    store=TaskStateStore()
    store.add(Task(id="t1",name="job",metadata={"tags":["safe"]}))
    items=store.all()
    items[0].metadata["tags"].append("mutated")
    assert store.get("t1").metadata["tags"]==["safe"]
