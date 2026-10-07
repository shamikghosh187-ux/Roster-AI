import pytest
from roster.result import OperationResult
def test_success_result():
    r=OperationResult.success({"status":"ok"}); assert r.ok and r.value["status"]=="ok" and r.error is None
def test_failure_result_requires_message():
    r=OperationResult.failure("denied"); assert not r.ok and r.error=="denied"
    with pytest.raises(ValueError): OperationResult.failure("")
