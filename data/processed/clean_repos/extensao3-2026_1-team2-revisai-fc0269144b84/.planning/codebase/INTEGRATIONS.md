# Integrations - RevisAI

Este documento detalha as integrações externas e serviços utilizados pelo RevisAI.

## External Services

### 1. Firebase (Google Cloud)
- **Service**: Firestore (NoSQL Database)
- **Library**: `firebase-admin`
- **Purpose**: Persistência de flashcards gerados, dados de usuários e logs de provedores.
- **Config Files**: `back-end/firebase.js`, `back-end/firebaseAdmin.js`.

### 2. OpenAI
- **Service**: Chat Completions (GPT-3.5-Turbo/GPT-4)
- **Library**: `openai`
- **Purpose**: Geração automatizada de flashcards a partir de prompts de texto.
- **Provider Class**: `OpenAIProvider` em `back-end/aiProvider.js`.

### 3. AWS Bedrock
- **Service**: Bedrock Runtime
- **Library**: `aws-sdk`
- **Purpose**: Provedor alternativo de IA (Claude, Llama, etc.).
- **Provider Class**: `AWSBedrockProvider` em `back-end/aiProvider.js`.

### 4. AWS SageMaker
- **Service**: SageMaker Runtime
- **Library**: `aws-sdk`
- **Purpose**: Integração com endpoints customizados de modelos de linguagem na AWS.
- **Provider Class**: `AWSSageMakerProvider` em `back-end/aiProvider.js`.

## Internal API (Backend to Frontend)
- **Endpoint**: `POST /api/generate-flashcards`
- **Endpoint**: `GET /api/flashcards/:userId`
- **Endpoint**: `GET /api/health`
- **CORS**: Habilitado via middleware `cors` para permitir requisições do frontend Vite.

## Environment Secrets
O sistema espera as seguintes chaves no arquivo `.env` do backend:
- `OPENAI_API_KEY`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `AI_PROVIDER` (opções: `openai`, `aws-bedrock`, `aws-sagemaker`)
- `FIREBASE_SERVICE_ACCOUNT` (ou credenciais implícitas via GCP)

---
*Last updated: 2026-05-11*
