from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from roster.execution_errors import ExecutionTimeout

def run_with_timeout(operation,timeout_seconds):
    if timeout_seconds<=0: raise ValueError("timeout must be positive")
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(operation)
        try: return future.result(timeout=timeout_seconds)
        except FutureTimeout as exc:
            future.cancel(); raise ExecutionTimeout("task execution timed out") from exc
