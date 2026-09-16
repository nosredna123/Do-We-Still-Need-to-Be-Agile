# 🤖 Chat Frontend - Backend Integration Guide

## Overview

O sistema de chat foi integrado com o FastAPI backend. A arquitetura funciona como:

```
Frontend (chat.html)
    ↓
Flask API (/api/chat)
    ↓
FastAPI Backend (POST /api/chat)
    ↓
LLM (OpenAI/Gemini)
```

---

## 🚀 Como Executar

### Pré-requisitos

1. **Python 3.12+** instalado
2. **PostgreSQL** rodando
3. **Variáveis de ambiente** configuradas (`.env`)

---

### 1️⃣ **Terminal 1: FastAPI Backend**

```bash
# Ativar ambiente virtual (se não estiver)
.\.venv\Scripts\Activate.ps1

# Instalar dependências (se não fez)
pip install -r requirements.txt

# Rodar FastAPI
uvicorn app.main:app --reload --port 8000
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### 2️⃣ **Terminal 2: Flask Frontend**

```bash
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Rodar Flask
python interface\app\app.py
```

**Output esperado:**
```
* Serving Flask app 'app'
* Running on http://127.0.0.1:5000
```

---

### 3️⃣ **Acessar a Interface**

Abra o navegador em:
```
http://127.0.0.1:5000/chat
```

---

## 📋 Endpoints

### FastAPI Chat Endpoint

**URL:** `POST http://127.0.0.1:8000/api/chat`

**Request:**
```json
{
  "message": "Olá, como você está?",
  "ia_id": 1,
  "history": [
    {
      "role": "user",
      "content": "Mensagem anterior"
    },
    {
      "role": "assistant",
      "content": "Resposta anterior"
    }
  ]
}
```

**Response (Success):**
```json
{
  "success": true,
  "response": "Resposta da IA aqui",
  "ia_name": "Julie",
  "error": null
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Descrição do erro",
  "response": "Erro ao processar sua mensagem"
}
```

---

### Flask Proxy Endpoint

**URL:** `POST http://127.0.0.1:5000/api/chat`

Faz forward para o FastAPI backend.

---

## 🔧 Configuração

### `.env`

```env
# Banco de dados
DATABASE_URL=postgresql://user:pass@localhost:5432/smartflow

# Criptografia
FERNET_KEY=sua-chave-aqui

# APIs de IA
OPENAI_API_KEY=sua-key-openai
GEMINI_API_KEY=sua-key-gemini
HUGGINGFACE_API_TOKEN=seu-token

# Backend FastAPI
FASTAPI_URL=http://127.0.0.1:8000
```

---

## 📝 Como Funciona

### 1. Usuário envia mensagem no chat

```javascript
// chat.js envia:
{
  "message": "Olá!",
  "ia_id": 1,
  "history": [...]
}
```

### 2. Flask recebe e forwarda para FastAPI

```python
# interface/app/app.py
requests.post(
    f'{fastapi_url}/api/chat',
    json={...}
)
```

### 3. FastAPI processa com LLM

```python
# app/routers/chat.py
llm = IAresponse(api_key, ia_model, system_prompt)
response = llm.generate_response(...)
```

### 4. Resposta volta ao frontend

```javascript
// chat.js exibe:
addMessage(data.response, 'bot');
```

---

## 🐛 Troubleshooting

### ❌ "Backend não disponível"

**Causa:** FastAPI não está rodando

**Solução:**
```bash
uvicorn app.main:app --reload --port 8000
```

---

### ❌ "IA não encontrada"

**Causa:** `ia_id` inválido

**Solução:**
- Verificar se existe IA com esse ID no banco de dados
- Usar ID de uma IA ativa existente

---

### ❌ "Nenhum prompt ativo"

**Causa:** IA sem prompt ativo

**Solução:**
1. Acesse `http://127.0.0.1:5000/`
2. Vá em "Prompts"
3. Crie/ative um prompt para a IA

---

### ❌ "API key não configurada"

**Causa:** IA sem credenciais OpenAI/Gemini

**Solução:**
1. Configure `OPENAI_API_KEY` ou `GEMINI_API_KEY` no `.env`
2. Edite a IA e adicione a API key

---

## 📚 Estrutura de Arquivos

```
interface/
├── app/
│   └── app.py           # Flask app com endpoint /api/chat
├── templates/
│   ├── chat.html        # UI do chat
│   └── ...
└── static/
    ├── js/
    │   └── chat.js      # Lógica do chat
    └── css/
        └── ...

app/
├── main.py              # FastAPI entry point
├── routers/
│   ├── webhook.py       # WhatsApp webhook
│   └── chat.py          # Chat endpoint
├── service/
│   └── llm_response.py  # Processamento com LLM
└── database/
    └── manipulations/
        └── ia_manipulations.py
```

---

## ✅ Fluxo Completo de Funcionamento

```
1. Usuário digita mensagem no chat
                ↓
2. JavaScript envia POST /api/chat (Flask)
                ↓
3. Flask valida e forwarda para FastAPI
                ↓
4. FastAPI busca IA no banco de dados
                ↓
5. FastAPI gera resposta com LLM
                ↓
6. FastAPI retorna resposta
                ↓
7. Flask retorna para JavaScript
                ↓
8. JavaScript exibe resposta no chat
```

---

## 🔐 Segurança

- ✅ Validação de entrada no backend
- ✅ Timeout de requisições (30s)
- ✅ Tratamento de erros com feedback ao usuário
- ✅ Histórico de mensagens no contexto da conversa

---

## 📖 Recursos Adicionais

- [FastAPI Docs](http://127.0.0.1:8000/docs) - Swagger UI
- [FastAPI ReDoc](http://127.0.0.1:8000/redoc) - ReDoc UI
- [README do Projeto](./README.md)
- [Interface README](./interface/README.md)

---

**Última atualização:** 31/05/2026
