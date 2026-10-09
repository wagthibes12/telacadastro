"""
auth_routes.py
Endpoints de autenticação: criação de usuário e login.
Mantido separado de routes.py (que é exclusivamente do domínio Cliente).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from .auth import criar_token_acesso, get_current_user
from .database import get_session
from .models import Usuario
from .schemas import LoginRequest, LoginResponse, UsuarioCreate, UsuarioRead
from .security import hash_senha, verificar_senha

router = APIRouter(tags=["Autenticação"])


@router.post(
    "/usuarios",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um usuário de acesso (e-mail + senha)",
)
def criar_usuario(dados: UsuarioCreate, session: Session = Depends(get_session)):
    novo_usuario = Usuario(email=dados.email, senha_hash=hash_senha(dados.senha))
    session.add(novo_usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com este e-mail.",
        )
    session.refresh(novo_usuario)
    return novo_usuario


@router.post("/login", response_model=LoginResponse, summary="Autentica um usuário")
def login(dados: LoginRequest, session: Session = Depends(get_session)):
    """
    A mensagem de erro é a MESMA tanto para "e-mail não existe" quanto para
    "senha errada" — evita que alguém descubra e-mails cadastrados só testando o login.
    """
    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()

    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="E-mail ou senha incorretos.",
    )

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise credenciais_invalidas

    token = criar_token_acesso(usuario.email)

    return LoginResponse(
        mensagem="Login realizado com sucesso.",
        email=usuario.email,
        access_token=token,
        token_type="bearer",
    )


@router.get(
    "/auth/me",
    response_model=UsuarioRead,
    summary="Valida se o token da aba atual ainda é aceito pelo servidor",
)
def obter_usuario_atual(usuario_atual: Usuario = Depends(get_current_user)):
    return usuario_atual