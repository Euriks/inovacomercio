from __future__ import annotations

import os
from typing import Any
import requests
from frontend.utils import session

BASE_URL = os.getenv("INOVA_API_URL", "http://localhost:5000/api/v1")
TIMEOUT = float(os.getenv("INOVA_API_TIMEOUT", "10"))
MODO_DEMO = os.getenv("INOVA_DEMO", "1") == "1"


class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _headers() -> dict[str, str]:
    h = {"Accept": "application/json"}
    token = session.get_token()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _request(method: str, path: str, **kwargs) -> Any:
    url = f"{BASE_URL}{path}"
    try:
        r = requests.request(method, url, headers=_headers(), timeout=TIMEOUT, **kwargs)
    except requests.RequestException as e:
        raise APIError(0, f"Falha de rede: {e}") from e

    if r.status_code == 401:
        session.clear_auth()
        raise APIError(401, "Sessão expirada. Faça login novamente.")
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise APIError(r.status_code, detail)
    if r.status_code == 204 or not r.content:
        return None
    return r.json()


def _demo_or_raise(method: str, path: str, demo_fn, **kwargs) -> Any:
    try:
        return _request(method, path, **kwargs)
    except APIError as e:
        if MODO_DEMO and (e.status_code == 0 or e.status_code >= 500):
            return demo_fn()
        raise


def login(email: str, senha: str) -> dict[str, Any]:
    payload = _demo_or_raise(
        "POST",
        "/auth/login",
        lambda: {
            "access_token": "demo-token",
            "expires_in": 3600,
            "usuario": {"nome": "Admin", "role": "admin"},
            "tenant_id": "demo",
        },
        json={"email": email, "senha": senha},
    )
    session.set_auth(payload)
    return payload


def renovar_sessao(refresh_token: str) -> dict[str, Any]:
    payload = _demo_or_raise(
        "POST",
        "/auth/refresh",
        lambda: {
            "access_token": "demo-token-renovado",
            "expires_in": 3600,
            "usuario": {"nome": "Admin", "role": "admin"},
            "tenant_id": "demo",
        },
        json={"refresh_token": refresh_token},
    )
    session.set_auth(payload)
    return payload


def dashboard_resumo() -> dict[str, Any]:
    return _demo_or_raise(
        "GET",
        "/dashboard/resumo",
        lambda: {
            "faturamento_mes": 482350.75,
            "ticket_medio": 87.42,
            "margem_media": 0.284,
            "rupturas_ativas": 14,
            "credito_verde_saldo": 3280.50,
            "variacao_mom": 0.071,
        },
    )


def precificacao_listar() -> list[dict[str, Any]]:
    return _demo_or_raise(
        "GET",
        "/precificacao",
        lambda: [
            {"produto": "Vinho Tinto Reservado 750ml", "custo": 25.00, "markup": 1.6, "preco_sugerido": 40.00, "margem": 0.375},
            {"produto": "Cerveja Artesanal IPA 500ml", "custo": 8.50, "markup": 1.7, "preco_sugerido": 14.45, "margem": 0.410},
            {"produto": "Queijo Mussarela Peça Kg", "custo": 32.00, "markup": 1.4, "preco_sugerido": 44.80, "margem": 0.285},
        ],
    )


def curva_abc() -> dict[str, Any]:
    return _demo_or_raise(
        "GET",
        "/curva-abc",
        lambda: {
            "top10": [
                {"codigo": "P001", "produto": "Vinho Tinto Reservado 750ml", "faturamento": 145000.00, "curva": "A", "participacao": 30.0},
                {"codigo": "P002", "produto": "Whisky 12 Anos", "faturamento": 98000.00, "curva": "A", "participacao": 20.3},
            ],
            "classes": [
                {"classe": "A", "faturamento": 243000.00},
                {"classe": "B", "faturamento": 110000.00},
                {"classe": "C", "faturamento": 35000.00},
            ]
        },
    )


def esg_indicadores() -> dict[str, Any]:
    return _demo_or_raise(
        "GET",
        "/esg/indicadores",
        lambda: {
            "ambiental": {"co2_evitado_kg": 1420.5, "residuos_kg": 450.0},
            "social": {"colaboradores": 24},
            "governanca": {"conformidade_pct": 0.98}
        },
    )


def auditoria_eventos(limit: int = 100) -> list[dict[str, Any]]:
    return _demo_or_raise(
        "GET",
        f"/auditoria/eventos?limit={limit}",
        lambda: [
            {"id": 1, "usuario": "Admin", "evento": "LOGIN", "modulo": "Auth", "ts": 1725450000},
            {"id": 2, "usuario": "Admin", "evento": "AJUSTE_ESTOQUE", "modulo": "Precificação", "ts": 1725451200}
        ],
    )