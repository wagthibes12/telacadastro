"""
models.py
Define as entidades de PERSISTÊNCIA (tabelas reais do MySQL).

Usa SQLModel para unir, numa única classe, o modelo ORM (SQLAlchemy) e a
tipagem de dados (Pydantic), evitando duplicar a definição de campos.
Esta camada é intencionalmente separada de schemas.py: aqui vive o que é
salvo no banco; em schemas.py vive o que trafega na API (podem divergir).
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Cliente(SQLModel, table=True):
    """Representa a tabela 'clientes' no MySQL."""

    __tablename__ = "clientes"

    id: Optional[int] = Field(default=None, primary_key=True)

    # unique=True garante a restrição de nome único também no nível do ORM
    # (o schema.sql reforça a mesma regra diretamente no banco).
    nome: str = Field(nullable=False, max_length=150, unique=True, index=True)

    email: str = Field(nullable=False, max_length=150)

    telefone: str = Field(nullable=False, max_length=20)
    cidade: str = Field(nullable=False, max_length=100)

    criado_em: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    atualizado_em: Optional[datetime] = Field(default=None)

class Usuario(SQLModel, table=True):
    """
    Representa a tabela 'usuarios' no MySQL — usada para autenticação (login).
    Guarda apenas o HASH da senha (nunca a senha em texto puro).
    """

    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, max_length=150, unique=True, index=True)
    senha_hash: str = Field(nullable=False, max_length=255)
    criado_em: datetime = Field(default_factory=datetime.utcnow, nullable=False)    
