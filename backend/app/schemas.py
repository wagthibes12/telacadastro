"""
schemas.py
Camada de VALIDAÇÃO de entrada e saída (DTOs — Data Transfer Objects).

Mantém o contrato público da API desacoplado do modelo de persistência
(models.py). Isso permite, por exemplo, mudar uma coluna do banco sem
quebrar o contrato da API, e vice-versa.
"""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class ClienteBase(BaseModel):
    """Campos e regras de validação comuns a criação e leitura."""

    nome: str
    email: EmailStr
    telefone: str
    cidade: str

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("O nome deve ter ao menos 2 caracteres.")
        return v

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, v: str) -> str:
        # Aceita formatos como "(49) 99999-9999" ou "49999999999"
        digitos = re.sub(r"\D", "", v)
        if not (10 <= len(digitos) <= 11):
            raise ValueError("Telefone inválido. Informe DDD + número (10 ou 11 dígitos).")
        return v.strip()

    @field_validator("cidade")
    @classmethod
    def validar_cidade(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("A cidade deve ter ao menos 2 caracteres.")
        return v


class ClienteCreate(ClienteBase):
    """Schema usado no corpo do POST /clientes (criação)."""
    pass


class ClienteUpdate(BaseModel):
    """
    Schema usado no corpo do PUT /clientes/{id}.
    Campos opcionais permitem atualização parcial de forma segura.
    """

    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cidade: Optional[str] = None


class ClienteRead(ClienteBase):
    """Schema de SAÍDA: o que a API efetivamente devolve ao cliente HTTP."""

    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    # Permite construir este schema a partir de um objeto ORM (Cliente)
    model_config = ConfigDict(from_attributes=True)

# =============================================================
# Schemas de autenticação (login)
# =============================================================

class LoginRequest(BaseModel):
    """
    Regras de senha aplicadas no validador:
      - mínimo 6 caracteres (via Field)
      - ao menos 1 letra maiúscula
      - ao menos 1 número
      - ao menos 1 caractere especial
    Se qualquer regra falhar, o Pydantic levanta ValidationError e o
    FastAPI converte automaticamente em HTTP 422.
    """

    email: EmailStr
    senha: str = Field(min_length=6, description="Senha do usuário")

    @field_validator("senha")
    @classmethod
    def validar_complexidade_senha(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula.")
        if not re.search(r"\d", v):
            raise ValueError("A senha deve conter ao menos um número.")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("A senha deve conter ao menos um caractere especial.")
        return v


class UsuarioCreate(LoginRequest):
    """Schema do POST /usuarios. Reaproveita as regras de LoginRequest (DRY)."""
    pass


class UsuarioRead(BaseModel):
    """Schema de SAÍDA ao criar um usuário — nunca inclui a senha/hash."""

    id: int
    email: EmailStr
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    mensagem: str
    email: EmailStr
    access_token: str
    token_type: str = "bearer"
