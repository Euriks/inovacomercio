from __future__ import annotations

class CompraService:
    @staticmethod
    def calcular_ponto_reposicao(consumo_medio_diario: float, lead_time: int) -> float:
        return consumo_medio_diario * lead_time
        
    @staticmethod
    def calcular_estoque_seguranca(consumo_medio_diario: float, lead_time_dias: int) -> float:
        return consumo_medio_diario * lead_time_dias * 1.2