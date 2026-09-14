from __future__ import annotations

import logging
import os
from typing import Any

import requests

from backend.app.services.fiscal.fiscal_settings import FORCE_CONTINGENCIA, FISCAL_MODE, NFE_PROVEDOR

logger = logging.getLogger(__name__)


class ContingencyService:
    """Decide se a emissão deve cair em contingência offline (sandbox ou corporativo)."""

    HEALTHCHECK_URL = os.getenv("NFE_HEALTHCHECK_URL", "")

    @staticmethod
    def deve_entrar_em_contingencia() -> bool:
        if FORCE_CONTINGENCIA or FISCAL_MODE == "OFFLINE":
            logger.info("Contingência forçada (FORCE_CONTINGENCIA/FISCAL_MODE).")
            return True

        try:
            return not ContingencyService._health_check_provedor()
        except Exception as exc:
            logger.warning("Health check fiscal falhou: %s", exc)
            return True

    @staticmethod
    def _health_check_provedor() -> bool:
        url = ContingencyService.HEALTHCHECK_URL
        if not url:
            # Ambiente de demonstração: provedor mock é considerado online.
            if NFE_PROVEDOR in {"mock", "sandbox"}:
                return True
            raise RuntimeError("URL de health check do provedor fiscal não configurada.")

        response = requests.get(url, timeout=3)
        response.raise_for_status()
        payload: Any = {}
        try:
            payload = response.json()
        except ValueError:
            return response.ok
        status = str(payload.get("status", "")).lower()
        return response.ok and status in {"", "ok", "online", "healthy"}
