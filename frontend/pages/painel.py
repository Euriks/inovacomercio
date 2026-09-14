from __future__ import annotations

import streamlit as st
import plotly.express as px
from frontend.api import client
from backend.app.services.fiscal.emission_service import EmissionService

def render() -> None:
    st.title("📊 Painel Executivo — InovaComércio MS")
    st.markdown("Visão geral em tempo real dos principais indicadores de desempenho do varejo de proximidade.")

    try:
        resumo = client.dashboard_resumo()
    except client.APIError as e:
        st.error(f"Erro ao carregar dados do painel: {e.detail}")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Faturamento do Mês",
            value=f"R$ {resumo.get('faturamento_mes', 0.0):,.2f}",
            delta=f"{resumo.get('variacao_mom', 0.0) * 100:+.1f}% (MoM)"
        )

    with col2:
        st.metric(
            label="Ticket Médio",
            value=f"R$ {resumo.get('ticket_medio', 0.0):,.2f}"
        )

    with col3:
        st.metric(
            label="Margem Média",
            value=f"{resumo.get('margem_media', 0.0) * 100:.1f}%"
        )

    with col4:
        st.metric(
            label="Rupturas Ativas (SKUs)",
            value=f"{resumo.get('rupturas_ativas', 0)}",
            delta="-3 vs ontem",
            delta_color="inverse"
        )

    st.divider()

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Evolução de Vendas (Últimos 7 Dias)")
        dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        valores = [68000, 72000, 75000, 81000, 94000, 115000, 98000]
        fig_vendas = px.line(
            x=dias, y=valores,
            labels={"x": "Dia da Semana", "y": "Faturamento (R$)"},
            markers=True, template="plotly_white"
        )
        st.plotly_chart(fig_vendas, use_container_width=True)

    with col_chart2:
        st.subheader("Distribuição por Categoria (Curva ABC)")
        categorias = ["Bebidas", "Mercearia", "Hortifrúti", "Limpeza", "Outros"]
        participacao = [42, 28, 15, 10, 5]
        fig_abc = px.pie(
            names=categorias, values=participacao,
            hole=0.4, template="plotly_white"
        )
        st.plotly_chart(fig_abc, use_container_width=True)

    st.divider()
    st.subheader("Dashboard Fiscal — NFC-e")
    fiscal = EmissionService.dashboard()
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("NFC-e Online", fiscal["nfce_online"])
    f2.metric("NFC-e Offline", fiscal["nfce_offline"])
    f3.metric("Pendentes", fiscal["pendentes"])
    f4.metric("Transmitidas", fiscal["transmitidas"])
    f5.metric("Autorizadas", fiscal["autorizadas"])

render()