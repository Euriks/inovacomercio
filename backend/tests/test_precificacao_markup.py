from decimal import Decimal
from app.services.precificacao_service import PrecificacaoService

def test_calculo_markup_divisor():
    custo = Decimal("40.00")
    impostos = Decimal("10.00")
    lucro = Decimal("20.00")
    custos_fixos = Decimal("10.00")
    
    preco_venda = PrecificacaoService.calcular_markup_divisor(custo, impostos, lucro, custos_fixos)
    assert preco_venda == Decimal("80.00")