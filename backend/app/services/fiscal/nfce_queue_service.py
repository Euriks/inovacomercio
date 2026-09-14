from __future__ import annotations

from typing import Any


class NFCeQueueService:
    """Fila local (outbox em memória) para transmissão posterior das NFC-e em contingência."""

    fila: list[dict[str, Any]] = []

    @classmethod
    def adicionar(cls, transacao: dict[str, Any]) -> dict[str, Any]:
        cls.fila.append(transacao)
        return transacao

    @classmethod
    def listar(cls) -> list[dict[str, Any]]:
        return list(cls.fila)

    @classmethod
    def pendentes(cls) -> list[dict[str, Any]]:
        return [n for n in cls.fila if n.get("status") in {"PENDENTE_TRANSMISSAO", "ASSINADA_LOCALMENTE", "CRIADA"}]

    @classmethod
    def atualizar(cls, chave_acesso: str, **campos: Any) -> dict[str, Any] | None:
        for nota in cls.fila:
            if nota.get("chave_acesso") == chave_acesso:
                nota.update(campos)
                return nota
        return None

    @classmethod
    def limpar(cls) -> None:
        cls.fila.clear()
