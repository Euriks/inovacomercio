from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.app.services.fiscal.contingency_service import ContingencyService
from backend.app.services.fiscal.nfce_queue_service import NFCeQueueService

logger = logging.getLogger(__name__)


class ReconciliationService:
    """Worker de reconciliação: transmite a fila local quando o provedor/SEFAZ volta."""

    @staticmethod
    def processar() -> dict[str, int]:
        transmitidas = 0
        autorizadas = 0
        rejeitadas = 0
        ainda_pendentes = 0

        ainda_offline = ContingencyService.deve_entrar_em_contingencia()

        for nota in NFCeQueueService.listar():
            if nota.get("status") not in {"PENDENTE_TRANSMISSAO", "ASSINADA_LOCALMENTE"}:
                continue
            if ainda_offline:
                ainda_pendentes += 1
                continue
            try:
                nota["status"] = "TRANSMITIDA"
                nota["dh_transmissao"] = datetime.now(timezone.utc).isoformat()
                transmitidas += 1
                # Sandbox: autorização imediata após transmissão
                nota["status"] = "AUTORIZADA"
                nota["protocolo"] = f"50{datetime.now(timezone.utc).strftime('%y%m%d')}{nota.get('numero', 0):09d}"
                autorizadas += 1
            except Exception as exc:
                logger.warning("Falha ao reconciliar NFC-e %s: %s", nota.get("chave_acesso"), exc)
                nota["status"] = "REJEITADA"
                nota["motivo"] = str(exc)
                rejeitadas += 1

        return {
            "transmitidas": transmitidas,
            "autorizadas": autorizadas,
            "rejeitadas": rejeitadas,
            "pendentes": ainda_pendentes,
        }
