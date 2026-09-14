from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.api import client
from frontend.utils import session
from backend.app.services.fiscal.emission_service import EmissionService
from backend.app.services.fiscal.fiscal_settings import FISCAL_MODE, FORCE_CONTINGENCIA
from backend.app.services.fiscal.nfce_queue_service import NFCeQueueService
from backend.app.services.fiscal.qr_code_service import QRCodeService
from backend.app.services.fiscal.reconciliation_service import ReconciliationService

if not session.is_authenticated():
    st.warning("Sessão expirada.")
    st.stop()

st.header("📄 NFC-e Offline (Contingência)")
st.caption(
    "Módulo fiscal de demonstração alinhado aos ADR-003, ADR-004 e ADR-005: "
    "assinatura local, QR Code, fila de transmissão, reconciliação e idempotência."
)

col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
col_cfg1.metric("FISCAL_MODE", FISCAL_MODE)
col_cfg2.metric("FORCE_CONTINGENCIA", "ATIVO" if FORCE_CONTINGENCIA else "desligado")
col_cfg3.metric("Pendentes", len(NFCeQueueService.pendentes()))

indicadores = EmissionService.dashboard()
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("NFC-e Online", indicadores["nfce_online"])
m2.metric("NFC-e Offline", indicadores["nfce_offline"])
m3.metric("Pendentes", indicadores["pendentes"])
m4.metric("Transmitidas", indicadores["transmitidas"])
m5.metric("Autorizadas", indicadores["autorizadas"])

st.divider()

tab_emitir, tab_fila, tab_recon = st.tabs(["Emitir venda", "Fila local", "Reconciliação"])

with tab_emitir:
    with st.form("form_nfce_offline"):
        venda_id = st.text_input("Identificador da venda", placeholder="V000123")
        numero = st.number_input("Número", min_value=1, value=1)
        serie = st.number_input("Série", min_value=1, value=1)
        valor_total = st.number_input("Valor total (R$)", min_value=0.01, value=87.42)
        emitir = st.form_submit_button("Concluir venda e gerar NFC-e")

    if emitir:
        try:
            transacao = client._demo_or_raise(
                "POST",
                "/fiscal/nfce/emitir",
                lambda: EmissionService.emitir(
                    {
                        "venda_id": venda_id or None,
                        "numero": int(numero),
                        "serie": int(serie),
                        "valor_total": float(valor_total),
                    }
                ),
                json={
                    "venda_id": venda_id or None,
                    "numero": int(numero),
                    "serie": int(serie),
                    "valor_total": float(valor_total),
                },
            )
            st.success(
                f"{transacao['status']} · {transacao['modo_emissao']} · chave {transacao['chave_acesso']}"
            )
            if transacao.get("idempotente"):
                st.info("Idempotência fiscal: esta venda já havia sido emitida.")
            png = QRCodeService.png_bytes(transacao["chave_acesso"], transacao["modo_emissao"])
            if png:
                st.image(png, caption="QR Code fiscal (sandbox)")
            with st.expander("XML assinado localmente"):
                st.code(transacao.get("xml") or "", language="xml")
        except client.APIError as e:
            st.error(f"Falha na emissão: {e.detail}")

with tab_fila:
    notas = NFCeQueueService.listar()
    if not notas:
        st.info("Nenhuma NFC-e na fila local.")
    else:
        df = pd.DataFrame(notas)
        colunas = [c for c in ["numero", "serie", "dh_emi", "modo_emissao", "status", "chave_acesso"] if c in df.columns]
        st.dataframe(df[colunas].rename(columns={
            "numero": "Número",
            "serie": "Série",
            "dh_emi": "Data",
            "modo_emissao": "Modo",
            "status": "Status",
            "chave_acesso": "Chave",
        }), use_container_width=True)

with tab_recon:
    if st.button("Processar fila (worker de reconciliação)"):
        resultado = ReconciliationService.processar()
        st.json(resultado)
    st.caption("Com FORCE_CONTINGENCIA=true as notas permanecem pendentes, simulando operação sem internet.")
