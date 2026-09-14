from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509

logger = logging.getLogger(__name__)

class CertificateMonitorService:
    """Serviço responsável por monitorar a validade de certificados digitais A1 (.pfx) para o módulo fiscal."""

    def __init__(self, cert_path: Optional[str] = None, cert_password: Optional[str] = None) -> None:
        self.cert_path = cert_path or os.getenv("NFE_CERT_PATH")
        self.cert_password = cert_password or os.getenv("NFE_CERT_PASSWORD")

    def verificar_validade(self) -> Dict[str, Any]:
        """Lê o arquivo .pfx, extrai a data de expiração do certificado x509 e calcula os dias restantes."""
        if not self.cert_path or not os.path.exists(self.cert_path):
            logger.warning("Caminho do certificado digital não configurado ou arquivo não encontrado: %s", self.cert_path)
            return {
                "status": "nao_encontrado",
                "mensagem": "Certificado digital não encontrado no caminho especificado.",
                "dias_restantes": None,
                "valido": False
            }

        if not self.cert_password:
            logger.error("Senha do certificado digital (.pfx) não informada.")
            return {
                "status": "erro_senha",
                "mensagem": "Senha do certificado digital não configurada.",
                "dias_restantes": None,
                "valido": False
            }

        try:
            with open(self.cert_path, "rb") as f:
                pfx_data = f.read()

            # Decodifica o arquivo PKCS12 (.pfx) utilizando a senha configurada
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                pfx_data, self.cert_password.encode("utf-8")
            )

            if not certificate:
                return {
                    "status": "erro_extracao",
                    "mensagem": "Não foi possível extrair o certificado do arquivo .pfx.",
                    "dias_restantes": None,
                    "valido": False
                }

            # Compatibilidade com Python datetime UTC
            not_before = (
                certificate.not_valid_after_utc 
                if hasattr(certificate, "not_valid_after_utc") 
                else certificate.not_valid_after.replace(tzinfo=timezone.utc)
            )
            
            agora = datetime.now(timezone.utc)
            delta = not_before - agora
            dias_restantes = delta.days

            # Extrai o nome comum (CN) do titular do certificado
            emitido_para = "Titular Desconhecido"
            for rdn in certificate.subject:
                if rdn.oid._name == "commonName":
                    emitido_para = rdn.value

            valido = dias_restantes > 0
            alerta_preventivo = dias_restantes <= 30 and valido

            if alerta_preventivo:
                logger.warning("ALERTA FISCAL: O certificado digital expira em %d dias (%s)!", dias_restantes, not_before.strftime("%Y-%m-%d"))
            elif not valido:
                logger.error("ERRO FISCAL: Certificado digital expirado em %s!", not_before.strftime("%Y-%m-%d"))

            return {
                "status": "alerta_expiracao" if alerta_preventivo else ("expirado" if not valido else "regular"),
                "emitido_para": emitido_para,
                "data_expiracao": not_before.isoformat(),
                "dias_restantes": dias_restantes,
                "valido": valido,
                "alerta_preventivo": alerta_preventivo,
                "mensagem": f"Certificado válido por mais {dias_restantes} dias." if valido else "Certificado digital expirado."
            }

        except Exception as e:
            logger.error("Falha ao analisar o certificado digital .pfx: %s", e)
            return {
                "status": "erro_processamento",
                "mensagem": f"Erro ao processar certificado: {str(e)}",
                "dias_restantes": None,
                "valido": False
            }

cert_monitor_service = CertificateMonitorService()