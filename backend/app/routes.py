"""
routes.py
Define os endpoints REST (CRUD) do recurso 'Cliente'.

Toda a lógica de acesso a dados fica isolada aqui, recebendo a sessão do
banco via injeção de dependência (get_session). Isso facilita testes
unitários (basta injetar uma sessão de teste/mock).
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from .database import get_session
from .models import Cliente
from .schemas import ClienteCreate, ClienteUpdate, ClienteRead

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "",
    response_model=ClienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo cliente",
)
def criar_cliente(dados: ClienteCreate, session: Session = Depends(get_session)):
    novo_cliente = Cliente(**dados.model_dump())
    session.add(novo_cliente)
    try:
        session.commit()
    except IntegrityError:
        # Disparado pela constraint UNIQUE do campo nome
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente cadastrado com este nome.",
        )
    session.refresh(novo_cliente)
    return novo_cliente


@router.get("", response_model=List[ClienteRead], summary="Lista todos os clientes")
def listar_clientes(session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).order_by(Cliente.id.desc())).all()
    return clientes


@router.get(
    "/{cliente_id}", response_model=ClienteRead, summary="Busca um cliente por ID"
)
def obter_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )
    return cliente


@router.put(
    "/{cliente_id}", response_model=ClienteRead, summary="Atualiza um cliente existente"
)
def atualizar_cliente(
    cliente_id: int, dados: ClienteUpdate, session: Session = Depends(get_session)
):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )

    # exclude_unset garante que só os campos enviados pelo cliente HTTP sejam alterados
    dados_atualizados = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizados.items():
        setattr(cliente, campo, valor)
    cliente.atualizado_em = datetime.utcnow()

    session.add(cliente)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente cadastrado com este nome.",
        )
    session.refresh(cliente)
    return cliente


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um cliente",
)
def deletar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )
    session.delete(cliente)
    session.commit()
    return None
