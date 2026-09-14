from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone

from backend.app.services.fiscal.fiscal_settings import CNPJ_EMITENTE, UF_CODIGO


def _mod11(base: str) -> str:
    pesos = list(range(2, 10))
    soma = 0
    idx = 0
    for char in reversed(base):
        soma += int(char) * pesos[idx % len(pesos)]
        idx += 1
    resto = soma % 11
    dv = 0 if resto in {0, 1} else 11 - resto
    return str(dv)


def gerar_chave_acesso(
    *,
    numero: int,
    serie: int = 1,
    cnpj: str = CNPJ_EMITENTE,
    uf: str = UF_CODIGO,
    modelo: str = "65",
    tp_emis: str = "9",
    agora: datetime | None = None,
) -> str:
    """Monta chave de acesso NFC-e (44 dígitos) com DV módulo 11."""
    agora = agora or datetime.now(timezone.utc)
    aamm = agora.strftime("%y%m")
    cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit()).zfill(14)[:14]
    serie_s = f"{int(serie):03d}"
    numero_s = f"{int(numero):09d}"
    cnf = f"{random.randint(0, 99999999):08d}"
    base = f"{uf}{aamm}{cnpj_limpo}{modelo}{serie_s}{numero_s}{tp_emis}{cnf}"
    return base + _mod11(base)


def xml_nfce_sandbox(transacao: dict) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<NFe xmlns="http://www.portalfiscal.inf.br/nfe">\n'
        "  <infNFe>\n"
        f"    <ide><mod>65</mod><nNF>{transacao['numero']}</nNF>"
        f"<serie>{transacao['serie']}</serie>"
        f"<tpEmis>{'9' if transacao.get('modo_emissao') == 'OFFLINE_CONTINGENCIA' else '1'}</tpEmis></ide>\n"
        f"    <emit><CNPJ>{CNPJ_EMITENTE}</CNPJ><xNome>InovaComércio MS</xNome></emit>\n"
        f"    <total><vNF>{transacao.get('valor_total', 0)}</vNF></total>\n"
        f"    <infAdic><chave>{transacao['chave_acesso']}</chave></infAdic>\n"
        "  </infNFe>\n"
        "</NFe>"
    )


def fingerprint_payload(payload: dict) -> str:
    raw = f"{payload.get('venda_id')}|{payload.get('numero')}|{payload.get('serie')}|{payload.get('valor_total')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
