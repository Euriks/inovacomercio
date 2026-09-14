from __future__ import annotations

from typing import Any


class IdempotencyService:
    """Garante que a mesma venda/chave não gere NFC-e duplicada (sandbox e corporativo)."""

    _registro: dict[str, dict[str, Any]] = {}

    @classmethod
    def chave(cls, venda_id: str | int | None, chave_acesso: str | None = None) -> str:
        if chave_acesso:
            return f"chave:{chave_acesso}"
        return f"venda:{venda_id}"

    @classmethod
    def ja_processada(cls, idem_key: str) -> bool:
        return idem_key in cls._registro

    @classmethod
    def obter(cls, idem_key: str) -> dict[str, Any] | None:
        return cls._registro.get(idem_key)

    @classmethod
    def registrar(cls, idem_key: str, transacao: dict[str, Any]) -> dict[str, Any]:
        cls._registro[idem_key] = transacao
        return transacao

    @classmethod
    def limpar(cls) -> None:
        cls._registro.clear()
