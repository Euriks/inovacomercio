from __future__ import annotations
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth_routes", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    tenant_id = data.get("tenant_id", "demo")
    
    if not username:
        return jsonify({"error": "Usuário obrigatório"}), 400

    permissions = [
        "produto.read",
        "produto.write",
        "nfe.emit",
        "analytics.view"
    ]
    
    access_token = create_access_token(
        identity={"username": username},
        additional_claims={
            "tenant_id": tenant_id,
            "permissions": permissions
        }
    )
    return jsonify({"access_token": access_token}), 200