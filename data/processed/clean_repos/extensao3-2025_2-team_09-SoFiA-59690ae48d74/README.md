# SoFiA

SoFiA é uma plataforma local para gestão financeira pessoal. Permite que usuários rastreiem, categorizem e analisem suas transações financeiras de forma intuitiva e eficiente através de um chat.

## Estrutura do Projeto



SoFiA/
├─ apps/
│ ├─ backend/ # Backend FastAPI
│ └─ frontend/ # Frontend React / T3 Stack
├─ scripts/
└─ README.md


## Requisitos

- Python 3.12
- Poetry
- Node.js (recomenda-se >=18)
- pnpm ou npm
- SQLite (ou outro banco, conforme configuração)

## Configuração do Backend

1. Entre na pasta do backend:

```bash
cd C:\Users\salet\SoFiA\apps\backend
```

Instale as dependências com Poetry:

 O projeto depende do ruff, que ainda não tem suporte oficial para Python 3.12. Para desenvolvimento rápido, comente a linha do ruff no pyproject.toml.

poetry install


Rode o backend:

poetry run uvicorn src.main:app --reload


O backend ficará disponível em: http://127.0.0.1:8000

Configuração do Frontend

Entre na pasta do frontend:

cd C:\Users\salet\SoFiA\apps\frontend


Crie o arquivo de variáveis de ambiente:

notepad .env.local


Cole o seguinte conteúdo:

# URL do backend FastAPI
VITE_API_BASE_URL=http://127.0.0.1:8000

# URL do frontend (para autenticação ou tRPC)
NEXTAUTH_URL=http://localhost:3000

# Banco de dados local (se necessário)
DATABASE_URL="sqlite:./dev.db"


Importante: VITE_API_BASE_URL precisa ser uma URL válida ou o frontend não irá iniciar.

Instale as dependências:

pnpm install
# ou npm install


Rode o frontend:

pnpm dev
# ou npm run dev


O frontend ficará disponível em: http://localhost:3000

Observações

Sempre rode o backend antes do frontend, para que o frontend consiga se conectar à API.

Se você quiser usar linting, depois ajuste o ruff quando houver suporte a Python 3.12.

Variáveis de ambiente adicionais podem ser necessárias dependendo de funcionalidades extras (tRPC, NextAuth, etc.).


Se você quiser, posso também **adicionar badges de status do projeto, versão e links rápidos** p
