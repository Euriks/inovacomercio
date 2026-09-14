from __future__ import annotations

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)