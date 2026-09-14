from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base


class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venda_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendas.id"), nullable=False)
    chave_acesso: Mapped[str] = mapped_column(String(44), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="autorizada", nullable=False)
    protocolo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    xml_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_emissao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )