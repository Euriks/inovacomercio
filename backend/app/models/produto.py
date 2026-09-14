from __future__ import annotations

from decimal import Decimal
from sqlalchemy import Numeric, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base
from __future__ import annotations
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Boolean
from app.models.base import Base, TimestampMixin

class Produto(Base, TimestampMixin):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True)
    codigo_barras = Column(String(50), unique=True)
    nome = Column(String(100), nullable=False)
    estoque_atual = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=0)
    preco_custo = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    preco_venda = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    ncm = Column(String(20))
    cest = Column(String(20))
    ativo = Column(Boolean, default=True)

    @property
    def margem_lucro(self) -> float:
        if not self.preco_venda or self.preco_venda <= 0:
            return 0.0
        custo = float(self.preco_custo or 0)
        venda = float(self.preco_venda)
        return round(((venda - custo) / venda) * 100, 2)