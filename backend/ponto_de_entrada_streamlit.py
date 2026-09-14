from __future__ import annotations

import streamlit as st
from frontend.utils import session, rbac
from frontend.api import client

# 1. Configuração mandatória no topo absoluto do script
st.set_page_config(
    page_title="InovaComércio MS | ERP Corporativo",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o estado de sessão de forma robusta
session.init_session()

# --- Fluxo de Autenticação Interrompido ------------------------------------
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

# --- Contexto do Usuário Autenticado ---------------------------------------
usuario = session.current_user()
role = session.current_role()
tenant = session.current_tenant()

# Interface Comum da Barra Lateral
st.sidebar.title("🏢 InovaComércio MS")
st.sidebar.markdown(f"**Usuário:** {usuario.get('nome', 'Gestor')}")
st.sidebar.markdown(f"**Papel:** `{role.upper()}` | **Tenant:** `{tenant}`")

if st.sidebar.button("Encerrar Sessão", use_container_width=True):
    session.clear_auth()
    st.rerun()

st.sidebar.divider()

# --- Mapeamento Declarativo de Páginas com Ícones e Títulos --------------
# Centraliza a definição de metadados das telas em uma estrutura limpa
todas_paginas = {
    "painel": st.Page("pages/painel.py", title="Painel Executivo", icon="📊", default=True),
    "precificacao": st.Page("pages/precificacao.py", title="Precificação & Markup", icon="💰"),
    "curva_abc": st.Page("pages/curva_abc.py", title="Curva ABC", icon="📈"),
    "forecast": st.Page("pages/previsão & Forecast", icon="🔮"),
    "credito_verde": st.Page("pages/credito_verde.py", title="Logística & Crédito Verde", icon="♻️"),
    "esg_dashboard": st.Page("pages/esg_dashboard.py", title="Dashboard ESG", icon="🌍"),
    "notas_fiscais": st.Page("pages/notas_fiscais.py", title="Documentos Fiscais", icon="🧾"),
    "auditoria": st.Page("pages/auditoria.py", title="Trilha de Auditoria", icon="📋"),
}

# --- Filtragem Baseada em Permissões (RBAC Dinâmico) ----------------------
# Cria uma lista contendo exclusivamente as páginas que a role atual pode visualizar
paginas_permitidas = [
    objeto_pagina 
    for chave, objeto_pagina in todas_paginas.items() 
    if rbac.verificar_permissao(role, chave)
]

# Fallback crítico de segurança: se nenhuma página for permitida, bloqueia a execução
if not paginas_permitidas:
    st.error("Erro crítico: Nenhuma permissão configurada para o seu perfil de usuário.")
    st.stop()

# --- Roteamento e Renderização Nativa --------------------------------------
# O Streamlit cria automaticamente os links nativos com estados visuais de foco corretos
nav = st.navigation(paginas_permitidas, position="sidebar")
nav.run()
