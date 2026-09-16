# FoodGuard

> Plataforma web que analisa rótulos de produtos alimentícios e avisa se eles são **seguros** para o seu perfil de saúde.

O **FoodGuard** cruza os ingredientes de um produto — obtidos por **leitura de código de barras** ou por **descrição em texto** — com a **anamnese** (histórico de saúde, alergias, intolerâncias e estilo alimentar) de cada usuário. A análise é feita por um assistente de IA (OpenAI GPT), que devolve um veredito de segurança com explicação técnica e o devido aviso médico.

Projeto desenvolvido na disciplina **Extensão III** — Curso de Ciência da Computação, Universidade Estadual do Ceará (UECE).

---

## Funcionalidades

- **Cadastro + Anamnese** — perfil de saúde obrigatório (doenças, medicamentos, alergias, intolerâncias, estilo alimentar). O acesso ao chat fica bloqueado até a anamnese ser concluída.
- **Análise por código de barras** — leitura via `BarcodeDetector` nativo do navegador, com _fallback_ para `zxing-wasm`; os dados do produto vêm da API pública [Open Food Facts](https://world.openfoodfacts.org/).
- **Análise por texto** — o usuário descreve o alimento e o assistente avalia com base no seu perfil.
- **Chat com contexto de saúde** — cada resposta da IA considera a anamnese do usuário, retornando um veredito de segurança (seguro / atenção / perigoso).
- **Galeria de conversas** — histórico em grade, com filtro por severidade do veredito, imagem do produto e exclusão de conversas.
- **Edição de perfil e anamnese** — alterar a anamnese invalida conversas antigas e força uma nova com o contexto atualizado.

---

## Arquitetura

Monorepo com dois aplicativos independentes:

```
extensao-3-projeto/
├── BACKEND/      → API REST (Django + DRF + PostgreSQL + OpenAI)
├── FRONTEND/     → SPA (React + TypeScript + Vite)
├── dataset/      → dados de apoio
└── documents/    → documentação do projeto
```

```
┌─────────────┐   HTTP/JWT    ┌──────────────┐   prompt+anamnese   ┌──────────────┐
│   Frontend  │ ────────────▶ │   Backend    │ ──────────────────▶ │ OpenAI GPT-4o│
│ React (SPA) │               │ Django REST  │                     │   (LLM)      │
└──────┬──────┘               └──────┬───────┘                     └──────────────┘
       │ barcode → ingredientes      │
       ▼                             ▼
┌──────────────┐              ┌──────────────┐
│ Open Food    │              │  PostgreSQL  │
│ Facts API    │              │  (anamnese,  │
└──────────────┘              │  chats, msgs)│
                              └──────────────┘
```

### Stack

| Camada       | Tecnologias                                                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| **Frontend** | React 19 · TypeScript 5.9 · Vite 8 · Tailwind CSS 3 · shadcn/ui + Radix · TanStack Query · Axios · React Router 7 · zxing-wasm |
| **Backend**  | Python 3.12 · Django 4.2 · Django REST Framework · PostgreSQL 16 · SimpleJWT · drf-spectacular (Swagger)                       |
| **IA**       | OpenAI (`gpt-4o`)                                                                                                              |
| **Infra**    | Docker + Docker Compose · VS Code Dev Containers                                                                               |

> Detalhes de organização interna: [`FRONTEND/frontend_architecture.md`](FRONTEND/frontend_architecture.md) e [`BACKEND/backend_architecture.md`](BACKEND/backend_architecture.md).

---

## Como rodar

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (com WSL2 no Windows)
- [Node.js](https://nodejs.org/) 20+ e npm
- Git
- Uma **chave da API da OpenAI** ([obtenha aqui](https://platform.openai.com/api-keys))

### 1. Clonar o repositório

```bash
git clone https://github.com/VictorManoel-Timbo/extensao-3-projeto.git
cd extensao-3-projeto
```

### 2. Backend (Django + PostgreSQL)

```bash
cd BACKEND
```

Crie os arquivos de ambiente em `BACKEND/.envs/.local/` (a pasta é ignorada pelo Git):

`.envs/.local/.postgres`

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=foodguard
POSTGRES_USER=postgres
POSTGRES_PASSWORD=uma_senha_segura
```

`.envs/.local/.django`

```env
DJANGO_SECRET_KEY=uma_chave_secreta_qualquer
AI_PROVIDER=openai
OPENAI_API_KEY=sua_chave_da_openai
OPENAI_MODEL_NAME=gpt-4o
```

Suba os containers e aplique as migrações:

```bash
docker compose -f docker-compose.local.yml up -d
docker compose -f docker-compose.local.yml exec django python manage.py migrate
```

Inicie o servidor (o container não sobe o servidor web sozinho):

```bash
docker compose -f docker-compose.local.yml exec -d django \
  sh -c "DJANGO_SETTINGS_MODULE=config.settings.local uvicorn config.asgi:application --host 0.0.0.0 --port 8000"
```

A API ficará disponível em **http://localhost:8000** · Swagger em **http://localhost:8000/api/docs/**.

> Alternativa: abrir a pasta `BACKEND/` no VS Code e usar **Dev Containers: Reopen in Container** (F1).

### 3. Frontend (React + Vite)

```bash
cd FRONTEND
cp .env.example .env   # ajuste VITE_BASE_URL se necessário
npm install
npm run dev
```

A aplicação abre em **http://localhost:5173** (Vite faz proxy de `/api` → backend e `/openfood` → Open Food Facts).

---

## Variáveis de ambiente

**Frontend** (`FRONTEND/.env`)
| Variável | Descrição |
|---|---|
| `VITE_BASE_URL` | URL do backend Django (ex.: `http://localhost:8000`) |
| `VITE_OPENFOOD_URL` | Endpoint da Open Food Facts |

**Backend** (`BACKEND/.envs/.local/`)
| Variável | Descrição |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta do Django (obrigatória) |
| `AI_PROVIDER` | Provedor de IA: `openai` ou `gemini` |
| `OPENAI_API_KEY` | Chave da API da OpenAI |
| `OPENAI_MODEL_NAME` | Modelo OpenAI (ex.: `gpt-4o`) |
| `POSTGRES_*` | Credenciais do PostgreSQL |

---

## Principais endpoints da API

Base: `/api`

| Método          | Rota                    | Descrição                                       |
| --------------- | ----------------------- | ----------------------------------------------- |
| `POST`          | `/auth/register/`       | Cadastro de usuário                             |
| `POST`          | `/auth/login/`          | Login por e-mail (retorna JWT access + refresh) |
| `POST`          | `/auth/token/refresh/`  | Renovação do token de acesso                    |
| `POST`          | `/auth/logout/`         | Logout (invalida o refresh token)               |
| `GET`           | `/auth/me/`             | Dados do usuário autenticado                    |
| `POST`          | `/anamnese/`            | Criar anamnese (uma por usuário)                |
| `GET` / `PATCH` | `/anamnese/me/`         | Obter / atualizar a própria anamnese            |
| `GET`           | `/chats/`               | Listar conversas do usuário                     |
| `DELETE`        | `/chats/<id>/`          | Excluir conversa                                |
| `POST`          | `/chats/message/send/`  | Enviar mensagem → análise da IA                 |
| `GET`           | `/chats/<id>/messages/` | Listar mensagens de uma conversa                |

A autenticação usa **JWT** (`Authorization: Bearer <access>`); o frontend renova o token automaticamente em respostas `401`.

---

## Privacidade (LGPD)

Os dados de anamnese são sensíveis e usados **exclusivamente** para compor o contexto enviado ao LLM e para visualização do próprio usuário. Não são compartilhados com terceiros nem com APIs de publicidade.
