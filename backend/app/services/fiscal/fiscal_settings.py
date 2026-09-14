from __future__ import annotations

import os


FISCAL_MODE = os.getenv("FISCAL_MODE", "SANDBOX").upper()
FORCE_CONTINGENCIA = os.getenv("FORCE_CONTINGENCIA", "false").lower() in {"1", "true", "yes", "on"}
NFE_PROVEDOR = os.getenv("NFE_PROVEDOR", "mock")
UF_CODIGO = os.getenv("NFE_UF_CODIGO", "50")  # Mato Grosso do Sul
CNPJ_EMITENTE = os.getenv("NFE_CNPJ_EMITENTE", "14283901000188")
CSC_ID = os.getenv("NFE_CSC_ID", "000001")
CSC_TOKEN = os.getenv("NFE_CSC_TOKEN", "DEMO-CSC-SANDBOX")
