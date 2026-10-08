import json
from roster.audit import AuditRecord
def test_audit_record_serializes_fields():
    data=json.loads(AuditRecord("open_app","allowed",request_id="abc").to_json())
    assert data["action"]=="open_app" and data["request_id"]=="abc" and data["timestamp"]


def test_audit_record_redacts_sensitive_detail():
    data=json.loads(AuditRecord("provider","failed",detail="Authorization: Bearer secret-token").to_json())
    assert "secret-token" not in data["detail"]
    assert "Bearer ***" in data["detail"]
