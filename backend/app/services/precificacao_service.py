from __future__ import annotations
from decimal import Decimal

class PrecificacaoService:
    @staticmethod
    def calcular_markup_divisor(
        custo: Decimal,
        impostos: Decimal,
        lucro: Decimal,
        custos_fixos: Decimal
    ) -> Decimal:
        percentual = (impostos + lucro + custos_fixos) / Decimal("100")
        divisor = Decimal("1") - percentual
        if divisor <= 0:
            raise ValueError("A soma dos percentuais não pode atingir ou superar 100%.")
        return (custo / divisor).quantize(Decimal("0.01"))