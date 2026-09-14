from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import Numeric, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base


class CreditoVerde(Base):
    __tablename__ = "creditos_verdes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    peso_residuos_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    co2_evitado_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_credito: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )