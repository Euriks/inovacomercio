from __future__ import annotations

import os

from backend.app.services.fiscal.chave_acesso import gerar_chave_acesso
from backend.app.services.fiscal.contingency_service import ContingencyService
from backend.app.services.fiscal.emission_service import EmissionService
from backend.app.services.fiscal.idempotency_service import IdempotencyService
from backend.app.services.fiscal.internal_signer import MockInternalSigner
from backend.app.services.fiscal.nfce_queue_service import NFCeQueueService
from backend.app.services.fiscal.reconciliation_service import ReconciliationService


def setup_function() -> None:
    NFCeQueueService.limpar()
    IdempotencyService.limpar()
    os.environ["FORCE_CONTINGENCIA"] = "true"
    os.environ["FISCAL_MODE"] = "SANDBOX"


def test_chave_acesso_tem_44_digitos() -> None:
    chave = gerar_chave_acesso(numero=12, serie=1, tp_emis="9")
    assert len(chave) == 44
    assert chave.isdigit()


def test_mock_signer_anexa_assinatura() -> None:
    xml = MockInternalSigner().sign_xml("<NFe />", "CERT-DEMO")
    assert "<AssinaturaMock" in xml
    assert "CERT-DEMO" in xml


def test_emissao_offline_entra_na_fila(monkeypatch) -> None:
    monkeypatch.setenv("FORCE_CONTINGENCIA", "true")
    monkeypatch.setattr(ContingencyService, "deve_entrar_em_contingencia", staticmethod(lambda: True))
    nota = EmissionService.emitir({"venda_id": "V1", "numero": 10, "serie": 1, "valor_total": 25.5})
    assert nota["modo_emissao"] == "OFFLINE_CONTINGENCIA"
    assert nota["status"] == "PENDENTE_TRANSMISSAO"
    assert len(NFCeQueueService.listar()) == 1


def test_idempotencia_nao_duplica(monkeypatch) -> None:
    monkeypatch.setattr(ContingencyService, "deve_entrar_em_contingencia", staticmethod(lambda: True))
    a = EmissionService.emitir({"venda_id": "V-IDEM", "numero": 1})
    b = EmissionService.emitir({"venda_id": "V-IDEM", "numero": 1})
    assert b["idempotente"] is True
    assert a["chave_acesso"] == b["chave_acesso"]
    assert len(NFCeQueueService.listar()) == 1


def test_reconciliacao_autoriza_quando_online(monkeypatch) -> None:
    monkeypatch.setattr(ContingencyService, "deve_entrar_em_contingencia", staticmethod(lambda: True))
    EmissionService.emitir({"venda_id": "V2", "numero": 2, "valor_total": 10})
    monkeypatch.setattr(ContingencyService, "deve_entrar_em_contingencia", staticmethod(lambda: False))
    resultado = ReconciliationService.processar()
    assert resultado["autorizadas"] == 1
    assert NFCeQueueService.listar()[0]["status"] == "AUTORIZADA"
