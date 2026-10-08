"""Thread-safe timeout wrapper for bounded callables."""
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from roster.execution_timeout_policy import TimeoutPolicy
class ExecutionTimedOut(TimeoutError): pass
def run_with_timeout(operation, policy: TimeoutPolicy, executor=None):
    owned=executor is None; pool=executor or ThreadPoolExecutor(max_workers=1); future=pool.submit(operation)
    try: return future.result(timeout=policy.seconds)
    except FutureTimeout as exc:
        future.cancel(); raise ExecutionTimedOut(f"execution exceeded {policy.seconds}s") from exc
    finally:
        if owned: pool.shutdown(wait=False, cancel_futures=True)
