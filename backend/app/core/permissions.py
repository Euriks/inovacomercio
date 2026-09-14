from __future__ import annotations

ADMIN_PERMISSIONS = ["produto.*", "nfe.*", "analytics.*", "audit.*", "tenant.*"]
GERENTE_PERMISSIONS = ["produto.read", "produto.write", "nfe.emit", "analytics.view"]
CAIXA_PERMISSIONS = ["venda.create", "produto.read"]
OPERADOR_PERMISSIONS = ["produto.read", "venda.create"]

PERFIS_PERMISSIONS = {
    "admin": ADMIN_PERMISSIONS,
    "gerente": GERENTE_PERMISSIONS,
    "caixa": CAIXA_PERMISSIONS,
    "operador": OPERADOR_PERMISSIONS
}