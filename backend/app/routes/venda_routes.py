from __future__ import annotations
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.audit_service import AuditService

venda_bp = Blueprint("venda_routes", __name__, url_prefix="/api/v1/vendas")

@venda_bp.route("", methods=["POST"])
@jwt_required()
def registrar_venda():
    data = request.get_json() or {}
    
    # Registro de auditoria corporativa da operação
    AuditService.registrar_evento(
        usuario_id=1,
        tenant_id=data.get("tenant_id", 1),
        evento="VENDA_REGISTRADA",
        modulo="Vendas"
    )
    
    return jsonify({"message": "Venda registrada com sucesso", "venda": data}), 201