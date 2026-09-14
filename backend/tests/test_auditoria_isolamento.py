def test_audit_log_model():
    from app.models.audit_log import AuditLog
    log = AuditLog(usuario_id=1, evento="LOGIN", modulo="Auth")
    assert log.usuario_id == 1
    assert log.evento == "LOGIN"