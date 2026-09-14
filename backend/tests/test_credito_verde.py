from decimal import Decimal
from app.services.credito_verde_service import CreditoVerdeService

def test_credito_verde():
    resultado = CreditoVerdeService.calcular("plastico", Decimal("10"))
    assert resultado == Decimal("8.00")

def test_calculo_co2():
    resultado = CreditoVerdeService.calcular_co2("papelao", Decimal("10"))
    assert resultado == Decimal("13.00")