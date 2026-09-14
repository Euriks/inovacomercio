from __future__ import annotations

import streamlit as st
import pandas as pd
from frontend.api import client
from frontend.utils import session

if not session.is_authenticated():
    st.warning("Sessão expirada.")
    st.stop()

st.header("🧾 Gestão Fiscal & Notas Fiscais")
st.caption("Emissão, consulta e cancelamento de NF-e/NFC-e integrado aos provedores oficiais.")

tab1, tab2 = st.tabs(["Emitir Nova Nota", "Notas Emitidas"])

with tab1:
    with st.form("form_nfe"):
        tipo_operacao = st.selectbox("Tipo de Documento", ["NFC-e (Consumidor)", "NF-e (Eletrônica)"])
        cliente_doc = st.text_input("CPF / CNPJ do Destinatário (Opcional)")
        valor_total = st.number_input("Valor Total da Nota (R$)", min_value=0.01, value=150.00)
        provedor = st.selectbox("Provedor Fiscal", ["NuvemFiscal", "FocusNFe", "Tecnospeed"])
        
        emitir = st.form_submit_button("Transmitir Documento Fiscal")

        if emitir:
            try:
                res = client._demo_or_raise(
                    "POST",
                    "/fiscal/emitir",
                    lambda: {"chave_acesso": "52260914283901000188550010000001231234567890", "status": "autorizada"}
                )
                st.success(f"Nota emitida com sucesso! Chave: {res.get('chave_acesso')}")
            except client.APIError as e:
                st.error(f"Erro na emissão fiscal: {e.detail}")

with tab2:
    st.subheader("Histórico de Transações Fiscais")
    st.info("Nenhuma nota fiscal registrada na sessão atual.")