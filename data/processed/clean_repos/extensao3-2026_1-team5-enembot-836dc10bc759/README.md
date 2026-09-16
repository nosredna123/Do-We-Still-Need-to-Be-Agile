# ENEMBot

Uma aplicação interativa para preparação do ENEM que combina um chat alimentado por LLM com um mecanismo inteligente de envio de questões organizadas por habilidade. A interface é baseada em chat com respostas por botões, cards de sugestões gerados por IA e um fluxo conversacional natural que incentiva o aprendizado autônomo.
# Funcionalidades Principais

Chat Interativo com Habilidades — Cada conversa ativa vincula-se a exatamente uma habilidade do ENEM + Redação. O usuário dispõe de um botão "Enviar Questão" que integra a questão ao fluxo do chat, mantendo o contexto da aprendizagem.

Respostas Guiadas e Educativas — Após o usuário responder, cards fixos com perguntas complementares são sugeridos para aprofundar o entendimento. A IA é programada para não revelar respostas prematuramente, incentivando o raciocínio do usuário.

Sugestões Contextualizadas — A aplicação oferece perguntas genéricas relacionadas ao assunto dentro do chat. Essas sugestões são dinamicamente geradas pela IA e servem como guia de aprendizado, permitindo que o usuário explore tópicos conexos antes de finalizar a questão.

# Links para visualização de artefatos gerados

**Documentos de Requisitos, FLuxos e estórias de usuário**

https://drive.google.com/drive/folders/1vJ2OqilobxDeF7XGFlK60K01md29TV9m?usp=sharing

**Apresentação 1**: 

https://canva.link/hs0kyh96g6xumx1

**Apresentação 2**

https://canva.link/zes3dcflj7v4suc


# Running the backend

## Requirements

### `uv`

To install `uv`, follow the steps below according to your operating system.

#### Linux
``` bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

``` bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing `uv`, clone the repository. 

```
git clone git@github.com:RenannLimaa/extensaoIII.git
```

Install the required packages for the project.

``` bash
cd backend

uv sync
```

Run the backend

``` bash
uv run uvicorn main:app --reload
```

### Using Docker
```
docker compose up --build
```

After running this command the first time, you can run the command below:
```
docker compose up
```

Access `http://localhost:8000/` and check if the returned message is `Hello World`. If it is, the project was correctly set up. 

# Running the frontend

## Requirements

### `npm`

This project uses a workspace at the repository root. Make sure you have Node.js and npm installed.

## Install dependencies

From the repository root:

```bash
npm install
```

## Run the frontend

From the repository root:

```bash
npm run dev
```

Or directly inside the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:3000/`.

## Build for production

From the repository root:

```bash
npm run build
```

## Start production mode

From the repository root:

```bash
npm run start
```
# .env
Segue esse modelo:
```
SUPABASE_URL = "url"
SUPABASE_KEY = "key"

GROQ_API_KEY = "key" #opcional
GEMINI_API_KEY = "key"
```
