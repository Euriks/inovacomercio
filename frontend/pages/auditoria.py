from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime
from frontend.api import client
from frontend.utils import session

if not session.is_authenticated():
    st.warning("Sessão expirada.")
    st.stop()

st.header("📋 Trilha de Auditoria Corporativa")
st.caption("Registro imutável de eventos, acessos e operações críticas do sistema.")

try:
    eventos = client._demo_or_raise(
        "GET",
        "/auditoria/eventos",
        lambda: [
            {"id": 1, "usuario": "Admin", "evento": "LOGIN", "modulo": "Auth", "ts": 1725450000},
            {"id": 2, "usuario": "Admin", "evento": "AJUSTE_ESTOQUE", "modulo": "Precificação", "ts": 1725451200}
        ]
    )
except client.APIError as e:
    st.error(f"Erro ao carregar logs de auditoria: {e.detail}")
    st.stop()

if not eventos:
    st.info("Nenhum evento registrado na trilha de auditoria.")
    st.stop()

df = pd.DataFrame(eventos)
if "ts" in df.columns:
    df["data_hora"] = df["ts"].apply(lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S") if x else "")

st.dataframe(df, use_container_width=True, hide_index=True)