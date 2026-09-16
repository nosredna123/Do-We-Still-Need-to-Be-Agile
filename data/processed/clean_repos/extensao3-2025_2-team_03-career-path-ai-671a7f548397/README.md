# Career-Path-AI
Repositório do CareerPath-AI.

## Descrição
Plataforma para análise de currículos, geração de trilhas de desenvolvimento em áreas da tecnologia e de guias de entrevista utilizando Google Gemini AI. A aplicação extrai informações de PDFs e fornece análise detalhada de habilidades, nível de experiência, recomendações de carreira e insights de mercado.

## Opção 1: Execução com Docker

### Pré-requisitos
- Docker
- Docker Compose
- Chave de API do Google Gemini

### Passos para execução:

#### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd career-path-ai
```

#### 2. Configure as variáveis de ambiente do Docker
```bash
cp .env.example .env
```

#### 3. Edite o arquivo .env
```env
POSTGRES_DB=seu_db
POSTGRES_USER=seu_user
POSTGRES_PASSWORD=sua_senha
```

#### 4. Configure as variáveis de ambiente do BackEnd
```bash
cd backend
cp .env.example .env.docker
```

#### 5. Edite o .env.docker
```env
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=

FRONTEND_HOST=http://localhost:5173

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_PORT=
MAIL_SERVER=
MAIL_STARTTLS=
MAIL_SSL_TLS=
MAIL_FROM=
USE_CREDENTIALS=

DEBUG=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=

GEMINI_API_KEY=
```

#### 6. Execute a aplicação
```bash
docker compose up --build
```

#### 7. Acesse a aplicação
- **API: http://localhost:8000
- **Swagger UI: http://localhost:8000/docs
- **Redoc: http://localhost:8000/redoc
- **FrontEnd: http://localhost:5173/login

## Funcionalidades
- ✅ Extração de texto de PDFs
- ✅ Análise de currículos com Google Gemini AI
- ✅ Detecção de habilidades técnicas
- ✅ Determinação de nível de experiência
- ✅ Recomendações de carreira personalizadas
- ✅ Identificação de lacunas de habilidades
- ✅ Insights de mercado

## Tecnologias Utilizadas
- **FastAPI** - Framework web moderno
- **Google Gemini AI** - IA generativa para análise
- **PyPDF2** - Extração de texto de PDFs
- **Python-dotenv** - Gerenciamento de variáveis de ambiente
- **Uvicorn** - Servidor ASGI
- **React** - Framework para FrontEnd