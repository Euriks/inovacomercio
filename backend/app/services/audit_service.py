from __future__ import annotations
from app.extensions import db
from app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def registrar_evento(usuario_id: int, evento: str, modulo: str, tenant_id: int | None = None, ip_address: str | None = None):
        log = AuditLog(
            usuario_id=usuario_id,
            tenant_id=tenant_id,
            evento=evento,
            modulo=modulo,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()