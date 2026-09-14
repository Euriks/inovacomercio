from __future__ import annotations

from decimal import Decimal

import streamlit as st

from backend.app.services.credito_verde_service import CreditoVerdeService
from frontend.utils import session

if not session.is_authenticated():
    st.warning("Sessão expirada.")
    st.stop()

st.header("♻️ Crédito Verde")
st.caption("Simulação de créditos por reciclagem no varejo de proximidade.")

material = st.selectbox("Material", ["papelao", "plastico", "aluminio"])
peso = st.number_input("Peso (kg)", min_value=0.1, value=2.0)
credito = CreditoVerdeService.calcular(material, Decimal(str(peso)))
co2 = CreditoVerdeService.calcular_co2(material, Decimal(str(peso)))

c1, c2 = st.columns(2)
c1.metric("Crédito estimado", f"R$ {credito}")
c2.metric("CO₂ evitado", f"{co2} kg")
