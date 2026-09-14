from __future__ import annotations

import streamlit as st
from frontend.utils import session
from frontend.api import client

# 1. Configuração da página deve ser o primeiro comando Streamlit executado
st.set_page_config(
    page_title="InovaComércio MS - Gestão, Fiscal & Sustentabilidade",
    page_icon="🛒",
    layout="wide",
)

# Inicializa o contêiner Pydantic no session_state
session.init_session()

# --- Fluxo de Autenticação -------------------------------------------------
if not session.is_authenticated():
    st.title("🚀 InovaComércio MS - Enterprise SaaS")
    st.caption("Plataforma Multi-Tenant de Varejo de Proximidade e Sustentabilidade")

    with st.form("login"):
        email = st.text_input("E-mail corporativo", value="admin@inovacomercio.ms")
        senha = st.text_input("Senha", type="password", value="admin123")
        submit = st.form_submit_button("Entrar no Sistema")

    if submit:
        try:
            # Assume-se que client.login internamente chama session.set_auth(payload)
            client.login(email, senha)
            st.success("Autenticado com sucesso! Carregando...")
            st.rerun()
        except client.APIError as e:
            st.error(f"Falha de autenticação: {e.detail}")
    
    # Interrompe a renderização do restante do script para usuários anônimos
    st.stop()

# --- Interface Protegida (Usuário Autenticado) -----------------------------

# Recupera o estado tipado via funções utilitárias para evitar quebras
tenant_atual = session.current_tenant()
role_atual = session.current_role()

# Acessa os dados do usuário com segurança através do objeto Pydantic da sessão
session_data = st.session_state.get(session._STATE_KEY)
nome_usuario = session_data.usuario.nome if (session_data and session_data.usuario) else "Operador"

# Barra Lateral de Navegação e Informações do Tenant
st.sidebar.title("🛒 InovaComércio MS")
st.sidebar.markdown(f"**Tenant:** `{tenant_atual}`")
st.sidebar.caption(f"Usuário: {nome_usuario} ({role_atual.upper()})")

if st.sidebar.button("Encerrar Sessão"):
    session.clear_auth()
    st.rerun()

# --- Definição de Páginas e Controle de Acesso (RBAC) ----------------------
# Lista base de páginas visíveis para qualquer usuário autenticado
paginas_validas = [
    st.Page("pages/painel.py", title="Visão Geral", icon="📊", default=True),
    st.Page("pages/precificacao.py", title="Precificação (Markup)", icon="💰"),
    st.Page("pages/curva_abc.py", title="Curva ABC", icon="📈"),
    st.Page("pages/forecast.py", title="Forecast & Rupturas", icon="🔮"),
    st.Page("pages/credito_verde.py", title="Crédito Verde", icon="♻️"),
    st.Page("pages/esg_dashboard.py", title="Painel ESG", icon="🌍"),
    st.Page("pages/notas_fiscais.py", title="Notas Fiscais", icon="🧾"),
    st.Page("pages/nfce_offline.py", title="NFC-e Offline", icon="📄"),
]

# Exemplo de Controle de Acesso Baseado em Nível (RBAC):
# A página de auditoria só é injetada no menu se o usuário for 'admin' ou 'auditor'
if role_atual in ("admin", "auditor"):
    paginas_validas.append(
        st.Page("pages/auditoria.py", title="Auditoria Corporativa", icon="📋")
    )

# Executa o roteamento nativo do Streamlit
nav = st.navigation(paginas_validas)
nav.run()
