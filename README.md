# Cadastro de Clientes

Sistema web de CRUD de clientes (Nome, E-mail, Telefone, Cidade), com separação
estrita de responsabilidades entre frontend e backend.

**Stack:** FastAPI + SQLModel + MySQL (backend) · HTML5 + CSS3 + Vanilla JS (frontend)

## Estrutura do projeto

```
cadastro-clientes/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py   # Conexão/engine/sessão do MySQL (+ túnel SSH)
│   │   ├── models.py     # Entidade ORM (SQLModel)
│   │   ├── schemas.py    # Validação de entrada/saída (Pydantic)
│   │   ├── routes.py     # Endpoints CRUD
│   │   └── main.py       # App FastAPI + CORS
│   ├── requirements.txt
│   ├── .env.example
│   └── .env              # Credenciais reais (NUNCA versionar)
├── database/
│   └── schema.sql        # Script SQL alternativo de criação manual
├── index.html             # Na raiz do projeto (fora de frontend/)
└── frontend/
    ├── css/styles.css
    └── js/
        ├── api.js         # Chamadas Fetch à API
        ├── dom.js         # Manipulação do DOM
        └── app.js         # Orquestração (eventos)
```

## 1. Banco de dados

Duas opções (escolha uma):

- **Automática (recomendada):** basta criar o banco vazio (`CREATE DATABASE cadastro_clientes;`)
  e deixar o próprio backend criar a tabela na inicialização, via
  `SQLModel.metadata.create_all()` (já implementado em `database.py`).
- **Manual:** execute `database/schema.sql` diretamente no MySQL.

## 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # depois edite com suas credenciais do MySQL

uvicorn app.main:app --reload --port 8000
```

### Conexão via túnel SSH

Se o seu MySQL só é acessível através de um servidor remoto (como no laboratório
do SENAC, via MySQL Workbench com "Standard TCP/IP over SSH"), o backend já
abre esse túnel automaticamente ao subir, usando a biblioteca `sshtunnel`.

No `.env`, mantenha `USE_SSH_TUNNEL=true` e preencha:

```
SSH_HOST=<ip do servidor SSH>
SSH_PORT=22
SSH_USER=<usuário SSH>
SSH_PASSWORD=<senha SSH>

DB_HOST=127.0.0.1     # host do MySQL relativo ao servidor SSH
DB_PORT=3306
DB_NAME=<schema>
DB_USER=<usuário MySQL>
DB_PASSWORD=<senha MySQL>
```

Se, em outro ambiente, o MySQL estiver acessível diretamente (sem túnel),
basta definir `USE_SSH_TUNNEL=false` e preencher `DB_HOST`/`DB_PORT` com o
endereço real do banco.

A API sobe em `http://127.0.0.1:8000`. Documentação interativa automática do
FastAPI (Swagger) em `http://127.0.0.1:8000/docs`.

### Endpoints

| Método | Rota              | Descrição                  |
|--------|-------------------|-----------------------------|
| POST   | /clientes         | Cria um cliente             |
| GET    | /clientes         | Lista todos os clientes     |
| GET    | /clientes/{id}    | Busca um cliente por ID     |
| PUT    | /clientes/{id}    | Atualiza um cliente         |
| DELETE | /clientes/{id}    | Remove um cliente           |

## 3. Frontend

`index.html` fica na raiz do projeto (fora da pasta `frontend/`), que contém
apenas `css/` e `js/`. Não requer build. Basta servir os arquivos estáticos a
partir da RAIZ do projeto (não de dentro de `frontend/`), por exemplo abrindo
"Open with Live Server" no `index.html` da raiz, ou:

```bash
# a partir da pasta raiz "cadastro-clientes"
python -m http.server 5500
```

Acesse `http://127.0.0.1:5500`. Se mudar a porta/host do frontend, adicione a
nova origem em `ORIGENS_PERMITIDAS` (backend/app/main.py) e em
`API_BASE_URL` (frontend/js/api.js) caso o backend também mude de endereço.

## Observações de produção

- Nunca versione o arquivo `.env` real — apenas `.env.example`.
- Ajuste `ORIGENS_PERMITIDAS` no `main.py` para os domínios reais em produção.
- Em produção, sirva o frontend por um servidor de arquivos estáticos/CDN e o
  backend atrás de um servidor ASGI como Uvicorn/Gunicorn + proxy reverso (Nginx).
