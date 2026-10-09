"""
auth.py
Lógica de geração e validação de token JWT (autenticação baseada em token).
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from .database import get_session
from .models import Usuario

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY não definido no .env. Gere um valor forte e único."
    )

# Quando o cabeçalho Authorization não vem na requisição, o HTTPBearer já
# responde 403 Forbidden sozinho (por isso o frontend trata 401 E 403).
esquema_bearer = HTTPBearer()


def criar_token_acesso(email_usuario: str) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": email_usuario,
        "iat": agora,
        "exp": agora + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada. Faça login novamente.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido."
        )


def get_current_user(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    session: Session = Depends(get_session),
) -> Usuario:
    payload = _decodificar_token(credenciais.credentials)
    email_usuario = payload.get("sub")

    if not email_usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: sem identificação de usuário.",
        )

    usuario = session.exec(
        select(Usuario).where(Usuario.email == email_usuario)
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário do token não existe mais.",
        )

    return usuario