from __future__ import annotations

from abc import ABC, abstractmethod


class InternalSigner(ABC):
    """Assinatura local do XML da NFC-e (A1 por estabelecimento na versão corporativa)."""

    @abstractmethod
    def sign_xml(self, xml: str, certificado_ref: str) -> str:
        raise NotImplementedError


class MockInternalSigner(InternalSigner):
    """Assinatura simulada para Colab, sandbox e MVP."""

    def sign_xml(self, xml: str, certificado_ref: str) -> str:
        ref = certificado_ref or "CERT-DEMO-A1"
        if "<AssinaturaMock" in xml:
            return xml
        return (
            xml.rstrip()
            + f'\n<AssinaturaMock certificado_ref="{ref}" algoritmo="RSA-SHA256-SIMULADO" />'
        )
