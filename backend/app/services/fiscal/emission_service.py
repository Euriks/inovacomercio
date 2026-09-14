from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from typing import Any

from backend.app.services.fiscal.chave_acesso import gerar_chave_acesso, xml_nfce_sandbox
from backend.app.services.fiscal.contingency_service import ContingencyService
from backend.app.services.fiscal.fiscal_settings import FISCAL_MODE
from backend.app.services.fiscal.idempotency_service import IdempotencyService
from backend.app.services.fiscal.internal_signer import MockInternalSigner
from backend.app.services.fiscal.nfce_queue_service import NFCeQueueService
from backend.app.services.fiscal.qr_code_service import QRCodeService

_NUMERADOR = count(1)


class EmissionService:
    """Orquestra venda → contingência → chave → assinatura local → QR → fila."""

    signer = MockInternalSigner()

    @classmethod
    def proximo_numero(cls) -> int:
        return next(_NUMERADOR)

    @classmethod
    def emitir(cls, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        venda_id = payload.get("venda_id") or f"V{cls.proximo_numero():06d}"
        numero = int(payload.get("numero") or cls.proximo_numero())
        serie = int(payload.get("serie") or 1)
        valor_total = float(payload.get("valor_total") or 0)
        certificado_ref = payload.get("certificado_ref") or "CERT-DEMO-A1-LOJA-01"

        idem_key = IdempotencyService.chave(venda_id)
        existente = IdempotencyService.obter(idem_key)
        if existente:
            return {**existente, "idempotente": True}

        agora = datetime.now(timezone.utc)
        offline = ContingencyService.deve_entrar_em_contingencia()
        modo = "OFFLINE_CONTINGENCIA" if offline else "ONLINE"
        tp_emis = "9" if offline else "1"
        chave = gerar_chave_acesso(numero=numero, serie=serie, tp_emis=tp_emis, agora=agora)

        transacao: dict[str, Any] = {
            "venda_id": venda_id,
            "numero": numero,
            "serie": serie,
            "valor_total": valor_total,
            "chave_acesso": chave,
            "modo_emissao": modo,
            "dh_emi": agora.isoformat(),
            "dh_transmissao": None,
            "status": "CRIADA",
            "fiscal_mode": FISCAL_MODE,
            "xml": "",
            "qr_payload": "",
            "protocolo": None,
            "idempotente": False,
        }

        xml = xml_nfce_sandbox(transacao)
        transacao["status"] = "ASSINADA_LOCALMENTE" if offline else "CRIADA"
        transacao["xml"] = cls.signer.sign_xml(xml, certificado_ref)
        transacao["qr_payload"] = QRCodeService.payload(chave, modo)

        if offline:
            transacao["status"] = "PENDENTE_TRANSMISSAO"
            NFCeQueueService.adicionar(transacao)
        else:
            transacao["status"] = "TRANSMITIDA"
            transacao["dh_transmissao"] = datetime.now(timezone.utc).isoformat()
            transacao["status"] = "AUTORIZADA"
            transacao["protocolo"] = f"50{agora.strftime('%y%m%d')}{numero:09d}"
            NFCeQueueService.adicionar(transacao)

        IdempotencyService.registrar(idem_key, transacao)
        IdempotencyService.registrar(IdempotencyService.chave(None, chave), transacao)
        return transacao

    @classmethod
    def dashboard(cls) -> dict[str, int]:
        notas = NFCeQueueService.listar()
        def qtd(*status: str) -> int:
            return sum(1 for n in notas if n.get("status") in status)

        return {
            "nfce_online": sum(1 for n in notas if n.get("modo_emissao") == "ONLINE"),
            "nfce_offline": sum(1 for n in notas if n.get("modo_emissao") == "OFFLINE_CONTINGENCIA"),
            "pendentes": qtd("PENDENTE_TRANSMISSAO", "ASSINADA_LOCALMENTE", "CRIADA"),
            "transmitidas": qtd("TRANSMITIDA", "AUTORIZADA"),
            "autorizadas": qtd("AUTORIZADA"),
            "rejeitadas": qtd("REJEITADA"),
            "canceladas": qtd("CANCELADA"),
            "total": len(notas),
        }
