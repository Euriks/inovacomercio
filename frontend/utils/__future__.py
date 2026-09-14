from __future__ import annotations

MATRIZ_ACESSO: dict[str, set[str]] = {
    "admin": {"*"},
    "gestor": {
        "painel", "precificacao", "curva_abc", "forecast",
        "credito_verde", "esg_dashboard"
    },
    "financeiro": {"painel", "notas_fiscais", "auditoria", "esg_dashboard"},
    "operador": {"painel", "credito_verde"}
}

def verificar_permissao(role: str, modulo: str) -> bool:
    """Verifica se o papel do usuário possui permissão para acessar o módulo."""
    role_limpo = (role or "operador").lower().strip()
    modulo_limpo = (modulo or "").lower().strip()

    permissoes = MATRIZ_ACESSO.get(role_limpo, MATRIZ_ACESSO["operador"])
    return "*" in permissoes or modulo_limpo in permissoes