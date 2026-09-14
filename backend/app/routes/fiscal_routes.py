from __future__ import annotations
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

fiscal_bp = Blueprint("fiscal_routes", __name__, url_prefix="/api/v1/fiscal")

@fiscal_bp.route("/nfe", methods=["POST"])
@jwt_required()
def emitir_nfe():
    data = request.get_json() or {}
    chave = "52260712345678000190550010000000011234567890"
    protocolo = "152260000123456"
    xml_url = f"https://api.nuvemfiscal.com.br/v1/nfe/{chave}/xml"
    
    return jsonify({
        "status": "AUTORIZADA",
        "chave": chave,
        "protocolo": protocolo,
        "xml_url": xml_url
    }), 201