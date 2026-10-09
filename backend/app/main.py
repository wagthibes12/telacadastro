"""
main.py
Ponto de entrada da aplicação FastAPI.

Responsabilidades desta camada (e só elas):
  - Instanciar o app;
  - Configurar CORS;
  - Registrar os routers;
  - Disparar a criação das tabelas na inicialização (lifespan).

Regras de negócio e acesso a dados NÃO devem viver aqui.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth_routes import router as auth_router
from .database import fechar_tunel_ssh
from .routes import router as clientes_router

# Origens autorizadas a consumir a API.
# Ajuste para o(s) domínio(s) real(is) do frontend em produção.
ORIGENS_PERMITIDAS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executado uma vez, na subida da aplicação."""
    
    yield
    # Encerra o túnel SSH aberto em database.py, liberando a conexão
    fechar_tunel_ssh()


app = FastAPI(
    title="API - Cadastro de Clientes",
    description="API REST para CRUD de clientes, construída com FastAPI + SQLModel.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes_router)
app.include_router(auth_router)


@app.get("/", tags=["Health"], summary="Health check")
def raiz():
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "online", "servico": "API Cadastro de Clientes"}
