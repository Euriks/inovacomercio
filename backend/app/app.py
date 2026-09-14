from __future__ import annotations

import streamlit as st
from frontend.utils import session, rbac
from frontend.api import client

st.set_page_config(
    page_title="InovaComércio MS | ERP Corporativo",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

session.init_session()

if not session.is_authenticated():
    st.title("🔐 InovaComércio MS — Autenticação")
    st.markdown("Entre com suas credenciais corporativas para acessar o ecossistema.")
    
    with st.form("form_login"):
        email = st.text_input("E-mail corporativo", value="gestor@inovacomercio.ms")
        senha = st.text_input("Senha", type="password", value="senha123")
        btn = st.form_submit_button("Entrar no Sistema")
        
        if btn:
            try:
                client.login(email, senha)
                st.success("Autenticação realizada com sucesso!")
                st.rerun()
            except client.APIError as e:
                st.error(f"Falha no login: {e.detail}")
    st.stop()

usuario = session.current_user()
role = session.current_role()
tenant = session.current_tenant()

st.sidebar.title("🏢 InovaComércio MS")
st.sidebar.markdown(f"**Usuário:** {usuario.get('nome', 'Gestor')}")
st.sidebar.markdown(f"**Papel:** `{role.upper()}` | **Tenant:** `{tenant}`")

if st.sidebar.button("Encerrar Sessão"):
    session.clear_auth()
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### Módulos do Sistema")

modulos_disponiveis = [
    ("Painel Executivo", "painel"),
    ("Precificação & Markup", "precificacao"),
    ("Curva ABC", "curva_abc"),
    ("Previsão & Forecast", "forecast"),
    ("Logística & Crédito Verde", "credito_verde"),
    ("Dashboard ESG", "esg_dashboard"),
    ("Documentos Fiscais", "notas_fiscais"),
    ("NFC-e Offline", "nfce_offline"),
    ("Trilha de Auditoria", "auditoria"),
]

modulo_escolhido = None
for nome, chave in modulos_disponiveis:
    if rbac.verificar_permissao(role, chave):
        if st.sidebar.button(nome, use_container_width=True):
            st.session_state["modulo_atual"] = chave

modulo_atual = st.session_state.get("modulo_atual", "painel")

if not rbac.verificar_permissao(role, modulo_atual):
    st.error("Você não possui permissão para acessar este módulo.")
    st.stop()

if modulo_atual == "painel":
    from frontend.pages import painel
elif modulo_atual == "precificacao":
    from frontend.pages import precificacao
elif modulo_atual == "curva_abc":
    from frontend.pages import curva_abc
elif modulo_atual == "forecast":
    from frontend.pages import forecast
elif modulo_atual == "credito_verde":
    from frontend.pages import credito_verde
elif modulo_atual == "esg_dashboard":
    from frontend.pages import esg_dashboard
elif modulo_atual == "notas_fiscais":
    from frontend.pages import notas_fiscais
elif modulo_atual == "nfce_offline":
    from frontend.pages import nfce_offline
elif modulo_atual == "auditoria":
    from frontend.pages import auditoria
else:
    st.info("Selecione um módulo no menu lateral.")