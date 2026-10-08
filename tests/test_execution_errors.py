from roster.execution_errors import ExecutionBlocked, ExecutionCancelled, ExecutionError, ExecutionTimeout

def test_execution_errors_share_runtime_error_contract():
    assert issubclass(ExecutionTimeout,ExecutionError)
    assert issubclass(ExecutionCancelled,ExecutionError)
    assert issubclass(ExecutionBlocked,ExecutionError)
