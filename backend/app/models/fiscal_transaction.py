from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class FiscalTransaction(Base):
    """Transação fiscal NFC-e (online ou contingência offline)."""

    __tablename__ = "fiscal_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venda_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vendas.id"), nullable=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    serie: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    chave_acesso: Mapped[str] = mapped_column(String(44), unique=True, index=True, nullable=False)
    modo_emissao: Mapped[str] = mapped_column(String(20), default="ONLINE", nullable=False)
    # ONLINE | OFFLINE_CONTINGENCIA
    dh_emi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    dh_transmissao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="CRIADA", nullable=False)
    # CRIADA | ASSINADA_LOCALMENTE | PENDENTE_TRANSMISSAO | TRANSMITIDA | AUTORIZADA | REJEITADA | CANCELADA
    xml: Mapped[str | None] = mapped_column(Text, nullable=True)
    protocolo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_total: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
