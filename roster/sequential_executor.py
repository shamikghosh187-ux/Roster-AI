from roster.task_dependencies import DependencyGraph

class SequentialExecutor:
    def __init__(self,execute): self.execute=execute
    def run(self,steps):
        graph=DependencyGraph()
        by_id={step.task.id:step for step in steps}
        for step in steps: graph.add(step.task.id,step.depends_on)
        completed=set(); results={}
        while len(completed)<len(steps):
            ready=graph.ready(completed)
            ready=[task_id for task_id in ready if task_id in by_id]
            if not ready: raise RuntimeError("plan has unresolved dependencies")
            task_id=ready[0]
            results[task_id]=self.execute(by_id[task_id])
            completed.add(task_id)
        return results
