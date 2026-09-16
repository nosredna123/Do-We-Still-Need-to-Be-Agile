# Backend - Sistema de Adesão Medicamentosa

Sistema backend em FastAPI para gerenciamento de lembretes de medicação e simplificação de bulas usando IA.

## 🏗️ Arquitetura

O sistema utiliza:
- **FastAPI** → Backend REST principal
- **LangChain** → Orquestração e pipeline RAG
- **Gemini API** → LLM para interpretação e simplificação
- **ChromaDB** → Armazenamento vetorial de bulas
- **Google Calendar API** → Criação automática de lembretes

## 📁 Estrutura do Projeto

```
Backend/
├── app/
│   ├── main.py                 # Aplicação FastAPI principal
│   ├── core/                   # Configurações e dependências
│   │   ├── config.py          # Variáveis de ambiente
│   │   ├── logger.py          # Sistema de logs
│   │   └── dependencies.py    # Dependências globais
│   ├── api/                   # Endpoints da API
│   │   └── routers/
│   │       ├── meds.py        # Endpoints de medicamentos
│   │       ├── reminders.py   # Endpoints de lembretes
│   │       └── healthcheck.py # Healthcheck
│   ├── services/              # Lógica de negócio
│   │   ├── rag_service.py     # 🔹 Pipeline RAG (LangChain + Gemini)
│   │   ├── vector_service.py  # 🔹 Vetorização de bulas
│   │   ├── google_service.py  # 🔹 Integração Google Calendar
│   │   └── scraper_service.py # 🔹 Busca web de bulas
│   ├── db/                    # Banco de dados
│   │   ├── chroma_client.py   # 🔹 Cliente ChromaDB
│   │   └── seed.py            # 🔹 Script de seed
│   ├── schemas/               # Schemas Pydantic
│   ├── models/                # Modelos ORM (se necessário)
│   └── utils/                 # Utilitários
│       ├── google_auth.py     # 🔹 Autenticação OAuth2
│       └── text_processing.py # 🔹 Processamento de texto
├── .env.example               # Exemplo de variáveis de ambiente
├── requirements.txt          # Dependências Python
├── Dockerfile               # Container Docker
├── docker-compose.yml       # Orquestração Docker
└── README.md               # Este arquivo
```

## 🚀 Executar Localmente

### Pré-requisitos

- Python 3.11+
- Variáveis de ambiente configuradas (copiar `.env.example` para `.env`)

### Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
- `GOOGLE_API_KEY`: Chave da API do Gemini
- `GOOGLE_CLIENT_ID`: ID do cliente OAuth2 do Google
- `GOOGLE_CLIENT_SECRET`: Secret do cliente OAuth2

### Executar

```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em:
- API: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

## 🐳 Executar com Docker

### Build e Run

```bash
# Build da imagem
docker build -t meds-backend .

# Executar container
docker run -p 8000:8000 --env-file .env meds-backend
```

### Docker Compose

```bash
# Executar com docker-compose
docker-compose up --build

# Executar em background
docker-compose up -d
```

## 📝 Endpoints da API

### Healthcheck
- `GET /health` - Verifica status da aplicação

### Medicamentos
- `POST /api/meds/simplify` - Simplifica bula de medicamento
- `GET /api/meds/search` - Busca informações sobre medicamento

### Lembretes
- `POST /api/reminders/create` - Cria lembretes no Google Calendar
- `GET /api/reminders/list` - Lista lembretes criados
- `DELETE /api/reminders/{reminder_id}` - Remove lembrete

## 🧠 Próximos Passos de Implementação

### 1. Vetorização de Bulas (`app/services/vector_service.py`)

Implementar:
- Carregamento de PDFs com LangChain loaders
- Text splitting otimizado
- Geração de embeddings (Gemini)
- Armazenamento no ChromaDB

### 2. Pipeline RAG (`app/services/rag_service.py`)

Implementar:
- Configuração do retriever LangChain com ChromaDB
- Busca semântica de chunks relevantes
- Prompts otimizados para simplificação
- Integração com Gemini API

### 3. Integração Google Calendar (`app/services/google_service.py`)

Implementar:
- Fluxo OAuth2 completo
- Criação de eventos recorrentes
- Conversão de frequência em regras RRULE
- Gerenciamento de eventos

### 4. Autenticação Google (`app/utils/google_auth.py`)

Implementar:
- Fluxo OAuth2
- Armazenamento seguro de tokens
- Refresh automático de tokens

### 5. Cliente ChromaDB (`app/db/chroma_client.py`)

Implementar:
- Inicialização do cliente persistente
- Criação/obtenção de collections
- Configuração de embeddings

### 6. Seed do Banco (`app/db/seed.py`)

Implementar:
- Processamento de PDFs de bulas
- Vetorização e armazenamento inicial
- Script executável

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app
```

## 📚 Documentação Adicional

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Calendar API](https://developers.google.com/calendar)

## 🔒 Segurança

- Nunca commite o arquivo `.env` com credenciais reais
- Use variáveis de ambiente em produção
- Configure CORS adequadamente
- Implemente autenticação JWT se necessário

## 📄 Licença

Este projeto é parte do Sistema de Adesão Medicamentosa.

