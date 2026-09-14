from __future__ import annotations

import streamlit as st
from frontend.api import client
from frontend.utils import session

if not session.is_authenticated():
    st.warning("Sessão expirada.")
    st.stop()

st.header("🌍 Painel ESG & Sustentabilidade Corporativa")
st.caption("Monitoramento de indicadores ambientais, sociais e de governança.")

try:
    esg = client._demo_or_raise(
        "GET",
        "/esg/indicadores",
        lambda: {
            "ambiental": {"co2_evitado_kg": 1420.5, "residuos_kg": 450.0},
            "social": {"colaboradores": 24},
            "governanca": {"conformidade_pct": 0.98}
        }
    )
except client.APIError as e:
    st.error(f"Erro ao carregar indicadores ESG: {e.detail}")
    st.stop()

amb = esg.get("ambiental", {})
soc = esg.get("social", {})
gov = esg.get("governanca", {})

col1, col2, col3 = st.columns(3)
col1.metric("CO₂ Evitado", f"{amb.get('co2_evitado_kg', 0):,} kg")
col2.metric("Colaboradores", str(soc.get('colaboradores', 0)))
col3.metric("Conformidade", f"{gov.get('conformidade_pct', 0)*100:.1f}%")

st.markdown("---")
st.subheader("Detalhamento de Impacto Ambiental")
st.json(amb)