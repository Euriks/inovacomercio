# backend/app/routes/auth.py
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from backend.app.schemas.usuario import UsuarioCreateSchema, UsuarioOutputSchema

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/v1/usuarios", methods=["POST"])
def criar_usuario():
    try:
        # 1. Valida o JSON recebido contra o Schema do Pydantic
        dados_entrada = UsuarioCreateSchema.model_validate(request.get_json())
        
        # [Lógica Omitida]: Salvar no banco via SQLAlchemy usando dados_entrada.model_dump()
        # registro_banco = UsuarioModel(...)
        
        # Mock de objeto de banco retornado
        from mock import MockUsuario
        usuario_salvo = MockUsuario(id="123", tenant_id="empresa-a", **dados_entrada.model_dump())

        # 2. Transforma o modelo do banco no contrato de saída seguro
        dados_saida = UsuarioOutputSchema.model_validate(usuario_salvo)
        
        # 3. Retorna o dicionário serializado limpo
        return jsonify(dados_saida.model_dump()), 201

    except ValidationError as e:
        # Captura erros de digitação, e-mail mal formado ou senhas curtas
        return jsonify({"erro": "Dados inválidos", "detalhes": e.errors()}), 420
