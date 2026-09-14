from __future__ import annotations

import time
from typing import Any, Optional
from pydantic import BaseModel, Field
import streamlit as st

class UsuarioSchema(BaseModel):
    id: str
    nome: str
    email: str
    role: str = "operador"
    tenant_id: str

class AuthSession(BaseModel):
    auth_token: Optional[str] = None
    refresh_token: Optional[str] = None
    auth_expira_em: Optional[float] = None
    usuario: Optional[UsuarioSchema] = None
    tenant_id: Optional[str] = None

_STATE_KEY = "auth_manager"

def init_session() -> None:
    """Inicializa o gerenciador de autenticação no session_state."""
    if _STATE_KEY not in st.session_state:
        st.session_state[_STATE_KEY] = AuthSession()

def _get_session() -> AuthSession:
    init_session()
    return st.session_state[_STATE_KEY]

def set_auth(payload: dict[str, Any]) -> None:
    """Valida o payload da API Flask e popula a sessão do Streamlit."""
    token = payload.get("access_token")
    if not token:
        raise ValueError("Payload sem access_token")

    expires_in = payload.get("expires_in")
    try:
        expires_in_int = int(expires_in) if expires_in is not None else None
    except (TypeError, ValueError):
        expires_in_int = None

    usuario_data = payload.get("usuario")
    if not usuario_data or not isinstance(usuario_data, dict):
        raise ValueError("Payload sem dados de usuário válidos")
    
    usuario = UsuarioSchema.model_validate(usuario_data)
    tenant_id = payload.get("tenant_id") or usuario.tenant_id

    if not tenant_id:
        clear_auth()
        raise ValueError("Payload sem tenant_id válido")

    st.session_state[_STATE_KEY] = AuthSession(
        auth_token=token,
        refresh_token=payload.get("refresh_token") or _get_session().refresh_token,
        auth_expira_em=time.time() + expires_in_int if expires_in_int else None,
        usuario=usuario,
        tenant_id=str(tenant_id)
    )

def clear_auth() -> None:
    """Limpa completamente os dados de autenticação."""
    st.session_state[_STATE_KEY] = AuthSession()

def get_token() -> Optional[str]:
    """Retorna o token JWT atual."""
    return _get_session().auth_token

def current_user() -> Optional[UsuarioSchema]:
    """Retorna o objeto Schema do usuário logado."""
    return _get_session().usuario

def current_tenant() -> str:
    """Retorna o tenant_id ativo ou 'demo' como fallback de segurança."""
    return _get_session().tenant_id or "demo"

def current_role() -> str:
    """Retorna a role do usuário formatada."""
    session = _get_session()
    if not session.usuario:
        return "operador"
    return session.usuario.role.lower()

def _executar_refresh_token(r_token: str) -> bool:
    """Consome a API Flask internamente para obter um novo access_token."""
    from frontend.api import client
    try:
        # A função do cliente deve disparar um POST para /api/v1/auth/refresh
        # com o cabeçalho 'Authorization: Bearer <refresh_token>'
        novo_payload = client.renovar_sessao(r_token)
        set_auth(novo_payload)
        return True
    except Exception:
        # Qualquer falha na renovação limpa a sessão forçando novo login
        clear_auth()
        return False

def is_authenticated() -> bool:
    """Verifica se o usuário está autenticado e gerencia a renovação pró-ativa."""
    session = _get_session()
    if not session.auth_token:
        return False
        
    if session.auth_expira_em and time.time() >= session.auth_expira_em:
        # 🔄 Se o token expirou mas temos o refresh_token, tenta renovar antes de derrubar
        if session.refresh_token:
            return _executar_refresh_token(session.refresh_token)
        
        clear_auth()
        return False
    return True

