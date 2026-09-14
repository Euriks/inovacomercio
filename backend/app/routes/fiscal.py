from __future__ import annotations

import logging
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import pybreaker

from flask import request

from backend.app.services.fiscal.cert_monitor_service import cert_monitor_service
from backend.app.services.fiscal.emission_service import EmissionService
from backend.app.services.fiscal.fiscal_settings import FISCAL_MODE, FORCE_CONTINGENCIA
from backend.app.services.fiscal.nfce_queue_service import NFCeQueueService
from backend.app.services.fiscal.qr_code_service import QRCodeService
from backend.app.services.fiscal.reconciliation_service import ReconciliationService

# Configuração do Circuit Breaker para chamadas externas (SEFAZ / Provedores)
# Falha se houverem 5 erros seguidos e abre por 30 segundos
sefaz_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
logger = logging.getLogger(__name__)

fiscal_bp = Blueprint("fiscal", __name__, url_prefix="/api/v1/fiscal")

@fiscal_bp.route("/certificado/status", methods=["GET"])
@jwt_required()  # 🛡️ Protege o endpoint contra acessos anônimos
def verificar_certificado():
    """
    Endpoint Flask para verificar o status e a validade do certificado digital A1 (.pfx).
    Isolado e filtrado pelo contexto do Tenant logado.
    """
    # 🔑 Extrai o tenant_id ou a identidade injetada no token JWT pelo login
    identity = get_jwt_identity() or {}
    tenant_id = identity.get("tenant_id")

    if not tenant_id:
        return jsonify({"status": "erro", "mensagem": "Contexto de Tenant não identificado no JWT."}), 400

    try:
        # 🏢 Passa o tenant_id para buscar e validar o certificado correspondente à empresa logada
        resultado = cert_monitor_service.verificar_validade(tenant_id=tenant_id)
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error("Erro na rota de verificação de certificado para o Tenant %s: %s", tenant_id, e)
        return jsonify({
            "status": "erro_interno",
            "mensagem": "Não foi possível validar o certificado digital no momento.",
            "valido": False
        }), 500

@fiscal_bp.route("/status", methods=["GET"])
@jwt_required()  # 🛡️ Mantém consistência de segurança corporativa
def status_provedor_fiscal():
    """
    Retorna o status atual do adaptador SEFAZ-MS utilizando Circuit Breaker para resiliência.
    """
    provedor = current_app.config.get("NFE_PROVEDOR", "mock")
    
    try:
        # ⚡ Protege o bloco de código que consome APIs externas/fiscais com o Breaker
        with sefaz_breaker:
            # Aqui entraria a chamada real de status (ex: nfeStatusServico)
            sefaz_status = "online"
            contingencia = False
            mensagem = f"Provedor {provedor} operando normalmente com SEFAZ-MS."
            
    except pybreaker.CircuitBreakerError:
        # Fallback automático caso o provedor ou SEFAZ estejam caídos
        sefaz_status = "indisponivel"
        contingencia = True
        mensagem = f"Circuito aberto: Provedor {provedor}/SEFAZ-MS instável. Sistema operando em contingência local."
        logger.warning("Circuit Breaker 'sefaz_breaker' foi aberto devido a falhas consecutivas.")

    return jsonify({
        "provedor": provedor,
        "sefaz_ms": sefaz_status,
        "contingencia_ativa": contingencia,
        "mensagem": mensagem
    }), 200


@fiscal_bp.route("/nfce/emitir", methods=["POST"])
@jwt_required()
def emitir_nfce():
    payload = request.get_json(silent=True) or {}
    transacao = EmissionService.emitir(payload)
    return jsonify(transacao), 201 if not transacao.get("idempotente") else 200


@fiscal_bp.route("/nfce/fila", methods=["GET"])
@jwt_required()
def listar_fila_nfce():
    return jsonify(NFCeQueueService.listar()), 200


@fiscal_bp.route("/nfce/reconciliar", methods=["POST"])
@jwt_required()
def reconciliar_nfce():
    resultado = ReconciliationService.processar()
    return jsonify({"resultado": resultado, "fila": NFCeQueueService.listar()}), 200


@fiscal_bp.route("/nfce/dashboard", methods=["GET"])
@jwt_required()
def dashboard_fiscal():
    return jsonify({
        "indicadores": EmissionService.dashboard(),
        "fiscal_mode": FISCAL_MODE,
        "force_contingencia": FORCE_CONTINGENCIA,
    }), 200


@fiscal_bp.route("/nfce/qr/<chave_acesso>", methods=["GET"])
@jwt_required()
def qr_nfce(chave_acesso: str):
    return jsonify({
        "chave_acesso": chave_acesso,
        "payload": QRCodeService.payload(chave_acesso),
    }), 200

