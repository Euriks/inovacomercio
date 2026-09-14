from __future__ import annotations

import streamlit as st
import pandas as pd
from frontend.api import client
from frontend.utils import session

if not session.is_authenticated():
    st.warning("Sessão expirada. Faça login novamente.")
    st.stop()

st.header("🔮 Previsão de Demanda (Forecast)")
st.caption("Projeção de vendas e análise preditiva de estoque baseada em histórico.")

try:
    dados = client.forecast()
except client.APIError as e:
    st.error(f"Erro ao carregar forecast: {e.detail}")
    st.stop()

if not dados:
    st.info("Nenhum dado de forecast disponível.")
    st.stop()

df = pd.DataFrame(dados)
st.dataframe(df, use_container_width=True, hide_index=True)