from __future__ import annotations
import pandas as pd

class CurvaABCService:
    @staticmethod
    def calcular_curva_abc(dados_produtos: list[dict]) -> pd.DataFrame:
        if not dados_produtos:
            return pd.DataFrame()
        df = pd.DataFrame(dados_produtos)
        if "faturamento" not in df.columns or df["faturamento"].sum() == 0:
            return pd.DataFrame()
            
        df = df.sort_values(by="faturamento", ascending=False).reset_index(drop=True)
        df["acumulado"] = df["faturamento"].cumsum()
        df["pct_acumulado"] = df["acumulado"] / df["faturamento"].sum() * 100
        
        def classificar(pct):
            if pct <= 80:
                return "A"
            elif pct <= 95:
                return "B"
            return "C"
            
        df["classe"] = df["pct_acumulado"].apply(classificar)
        return df