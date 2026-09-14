from __future__ import annotations

import streamlit as st
import pandas as pd
from frontend.api import client

def render() -> None:
    st.title("💲 Precificação & Markup — InovaComércio MS")
    st.markdown("Gestão inteligente de margens, custos e formação de preço sugerido com base em markup divisor.")

    try:
        produtos = client.precificacao_listar()
    except client.APIError as e:
        st.error(f"Erro ao carregar lista de precificação: {e.detail}")
        produtos = []

    if produtos:
        df = pd.DataFrame(produtos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado no momento.")

    st.divider()

    st.subheader("Simulador de Markup Divisor")
    with st.form("form_simulador"):
        col1, col2, col3 = st.columns(3)
        with col1:
            custo_produto = st.number_input("Custo de Aquisição (R$)", min_value=0.01, value=25.00, step=1.00)
        with col2:
            markup_desejado = st.number_input("Markup Aplicado", min_value=1.0, value=1.60, step=0.05)
        with col3:
            impostos_pct = st.number_input("Carga Tributária Média (%)", min_value=0.0, max_value=100.0, value=12.0, step=1.0)

        btn_calcular = st.form_submit_button("Simular Preço de Venda")

        if btn_calcular:
            preco_sugerido = custo_produto * markup_desejado
            lucro_estimado = preco_sugerido - custo_produto - (preco_sugerido * (impostos_pct / 100))
            margem_liquida = (lucro_estimado / preco_sugerido) if preco_sugerido > 0 else 0.0

            st.success(f"**Preço Sugerido de Venda:** R$ {preco_sugerido:,.2f}")
            st.info(f"**Lucro Estimado por Unidade:** R$ {lucro_estimado:,.2f} | **Margem Líquida:** {margem_liquida * 100:.1f}%")

render()