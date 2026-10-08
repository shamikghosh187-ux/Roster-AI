class ExecutionError(RuntimeError): pass
class ExecutionTimeout(ExecutionError): pass
class ExecutionCancelled(ExecutionError): pass
class ExecutionBlocked(ExecutionError): pass
