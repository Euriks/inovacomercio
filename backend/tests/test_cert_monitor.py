from __future__ import annotations

import pytest
from backend.app.services.fiscal.cert_monitor_service import CertificateMonitorService


def test_certificado_nao_encontrado() -> None:
    """Verifica se o serviço trata corretamente o cenário de arquivo .pfx ausente."""
    service = CertificateMonitorService(cert_path="caminho/inexistente/certificado.pfx", cert_password="senha123")
    resultado = service.verificar_validade()
    
    assert resultado["status"] == "nao_encontrado"
    assert resultado["valido"] is False
    assert resultado["dias_restantes"] is None
    assert "não encontrado" in resultado["mensagem"].lower()


def test_senha_nao_informada(tmp_path) -> None:
    """Verifica se o serviço identifica a ausência da senha do certificado."""
    d = tmp_path / "certs"
    d.mkdir()
    pfx_fake = d / "temp.pfx"
    pfx_fake.write_bytes(b"conteudo_falso_pfx")
    
    service = CertificateMonitorService(cert_path=str(pfx_fake), cert_password="")
    resultado = service.verificar_validade()
    
    assert resultado["status"] == "erro_senha"
    assert resultado["valido"] is False
    assert resultado["dias_restantes"] is None
    assert "senha" in resultado["mensagem"].lower()


def test_processamento_arquivo_invalido(tmp_path) -> None:
    """Verifica se o serviço captura exceções de decodificação ao receber um arquivo corrompido."""
    d = tmp_path / "certs"
    d.mkdir()
    pfx_corrompido = d / "corrompido.pfx"
    pfx_corrompido.write_bytes(b"bytes_aleatorios_nao_pkcs12")
    
    service = CertificateMonitorService(cert_path=str(pfx_corrompido), cert_password="senha_valida")
    resultado = service.verificar_validade()
    
    assert resultado["status"] == "erro_processamento"
    assert resultado["valido"] is False
    assert resultado["dias_restantes"] is None
