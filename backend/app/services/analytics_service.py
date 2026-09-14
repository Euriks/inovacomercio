from __future__ import annotations

class AnalyticsService:
    @staticmethod
    def forecast_demanda(historico: list[float]) -> list[float]:
        if not historico:
            return []
        if len(historico) < 3:
            return historico

        media = sum(historico[-3:]) / 3

        return [
            round(media * 1.05, 2),
            round(media * 1.08, 2),
            round(media * 1.10, 2)
        ]