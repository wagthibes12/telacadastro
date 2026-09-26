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
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


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
