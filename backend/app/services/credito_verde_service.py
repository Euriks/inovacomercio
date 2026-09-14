from __future__ import annotations
from decimal import Decimal

class CreditoVerdeService:
    FATORES = {
        "papelao": Decimal("0.50"),
        "plastico": Decimal("0.80"),
        "aluminio": Decimal("2.50")
    }

    FATOR_CO2 = {
        "papelao": Decimal("1.30"),
        "plastico": Decimal("2.10"),
        "aluminio": Decimal("8.50")
    }

    @classmethod
    def calcular(cls, material: str, peso: Decimal) -> Decimal:
        fator = cls.FATORES.get(material.lower(), Decimal("0.10"))
        return (peso * fator).quantize(Decimal("0.01"))

    @classmethod
    def calcular_co2(cls, material: str, peso: Decimal) -> Decimal:
        fator = cls.FATOR_CO2.get(material.lower(), Decimal("0.50"))
        return (peso * fator).quantize(Decimal("0.01"))