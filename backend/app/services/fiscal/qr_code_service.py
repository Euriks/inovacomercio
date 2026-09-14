from __future__ import annotations

import hashlib
import io
from typing import Any

from backend.app.services.fiscal.fiscal_settings import CSC_ID, CSC_TOKEN, UF_CODIGO


class QRCodeService:
    """Gera payload e imagem de QR Code fiscal (sandbox). Em produção: URL SEFAZ + CSC + hash + chave."""

    @staticmethod
    def payload(chave_acesso: str, modo: str = "OFFLINE_CONTINGENCIA") -> str:
        digest = hashlib.sha1(f"{chave_acesso}{CSC_TOKEN}".encode("utf-8")).hexdigest()
        base = f"https://www.fazenda.ms.gov.br/nfce/qrcode"
        return (
            f"{base}?p={chave_acesso}|2|2|{CSC_ID}|{digest[:40]}"
            f"|uf={UF_CODIGO}|modo={modo}"
        )

    @staticmethod
    def gerar(chave_acesso: str, modo: str = "OFFLINE_CONTINGENCIA") -> Any:
        payload = QRCodeService.payload(chave_acesso, modo)
        try:
            import qrcode
        except ImportError:
            return payload

        img = qrcode.make(payload)
        return img

    @staticmethod
    def png_bytes(chave_acesso: str, modo: str = "OFFLINE_CONTINGENCIA") -> bytes | None:
        img = QRCodeService.gerar(chave_acesso, modo)
        if isinstance(img, (bytes, bytearray)):
            return bytes(img)
        if isinstance(img, str):
            return None
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
