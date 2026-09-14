from __future__ import annotations

import streamlit as st
import pandas as pd
from frontend.api import client
from frontend.utils import session

if not session.is_authenticated():
    st.warning("Sessão expirada. Faça login novamente.")
    st.stop()

st.header("📈 Curva ABC de Produtos")
st.caption("Classificação de inventario por relevância de faturamento (Curva ABC).")

try:
    dados = client.curva_abc()
except client.APIError as e:
    st.error(f"Erro ao carregar Curva ABC: {e.detail}")
    st.stop()

if not dados:
    st.info("Nenhum dado disponível para a Curva ABC.")
    st.stop()

df = pd.DataFrame(dados)
st.dataframe(df, use_container_width=True, hide_index=True)