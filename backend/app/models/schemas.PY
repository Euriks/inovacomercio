# backend/app/schemas/usuario.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

class UsuarioCreateSchema(BaseModel):
    """Valida o payload recebido na rota de criação/registro."""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr  # Validação nativa de e-mail real
    senha: str = Field(..., min_length=8)
    role: str = "operador"

class UsuarioOutputSchema(BaseModel):
    """Contrato de saída segura. Exclui o hash da senha automaticamente."""
    id: str
    tenant_id: str
    nome: str
    email: EmailStr
    role: str

    class ConfigDict:
        # Permite carregar dados direto do modelo do SQLAlchemy: UsuarioOutputSchema.model_validate(usuario_model)
        from_attributes = True
