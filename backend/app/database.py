"""
database.py
Responsável EXCLUSIVAMENTE pela configuração da conexão com o banco MySQL.

Neste ambiente, o MySQL não é acessível diretamente pela rede: ele só
"escuta" em 127.0.0.1 dentro do servidor remoto, então o acesso precisa
passar por um túnel SSH (o mesmo esquema usado na conexão do MySQL
Workbench: "Standard TCP/IP over SSH"). Por isso, além do SQLModel/engine,
este módulo também é responsável por abrir esse túnel quando necessário.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.engine import URL
from sshtunnel import SSHTunnelForwarder

# Carrega variáveis do arquivo .env (NUNCA versionar o .env real, apenas o .env.example)
load_dotenv()

# --- Parâmetros do túnel SSH ---
USE_SSH_TUNNEL = os.getenv("USE_SSH_TUNNEL", "true").lower() == "true"
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

# --- Parâmetros do MySQL (relativos ao servidor remoto, atrás do túnel) ---
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "aluno18")
DB_USER = os.getenv("DB_USER", "aluno18")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Referência ao túnel ativo, para poder encerrá-lo no shutdown da aplicação
_tunel_ssh: Optional[SSHTunnelForwarder] = None


def _abrir_tunel_ssh() -> int:
    """
    Abre o túnel SSH até o servidor remoto e encaminha uma porta local
    até a porta do MySQL dentro dele. Retorna a porta LOCAL a ser usada
    na string de conexão do SQLAlchemy.
    """
    global _tunel_ssh

    if _tunel_ssh is not None and _tunel_ssh.is_active:
        return _tunel_ssh.local_bind_port

    _tunel_ssh = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(DB_HOST, DB_PORT),
    )
    _tunel_ssh.start()
    return _tunel_ssh.local_bind_port


def _montar_database_url():
    """
    Monta a URL de conexão do SQLAlchemy/PyMySQL usando URL.create, que
    escapa automaticamente caracteres especiais na senha/usuário (ex.: @, :, /),
    evitando que eles quebrem o formato da string de conexão.
    """
    if USE_SSH_TUNNEL:
        porta_local = _abrir_tunel_ssh()
        return URL.create(
            drivername="mysql+pymysql",
            username=DB_USER,
            password=DB_PASSWORD,
            host="127.0.0.1",
            port=porta_local,
            database=DB_NAME,
        )

    return URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )


# echo=False em produção (evita logar SQL sensível, inclusive dados de clientes);
# pool_pre_ping evita erros de "conexão perdida" em conexões ociosas por muito tempo.
engine = create_engine(_montar_database_url(), echo=False, pool_pre_ping=True)


def create_db_and_tables() -> None:
    """
    Cria as tabelas com base nos modelos SQLModel registrados (models.py).
    Deve ser chamada uma única vez, na inicialização da aplicação (main.py).

    Observação: o SCHEMA (banco em si) deve existir previamente no MySQL —
    ver database/schema.sql. Esta função cria apenas as TABELAS dentro dele.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency do FastAPI: gera uma sessão por requisição e garante o
    fechamento correto (context manager), evitando vazamento de conexões.
    """
    with Session(engine) as session:
        yield session


def fechar_tunel_ssh() -> None:
    """
    Encerra o túnel SSH, se estiver ativo. Deve ser chamado no shutdown
    da aplicação (ver lifespan em main.py) para não deixar conexões presas.
    """
    global _tunel_ssh
    if _tunel_ssh is not None and _tunel_ssh.is_active:
        _tunel_ssh.stop()
        _tunel_ssh = None