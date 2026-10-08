from concurrent.futures import ThreadPoolExecutor

class ParallelExecutor:
    def __init__(self,execute,max_workers=4):
        if max_workers<1: raise ValueError("max_workers must be positive")
        self.execute=execute; self.max_workers=max_workers
    def run(self,steps):
        with ThreadPoolExecutor(max_workers=self.max_workers,thread_name_prefix="roster-task") as pool:
            futures={step.task.id:pool.submit(self.execute,step) for step in steps}
            return {task_id:future.result() for task_id,future in futures.items()}
