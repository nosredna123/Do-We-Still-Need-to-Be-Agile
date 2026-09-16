# EstudaAI

Este projeto foi feito para a disciplina de Extensão 3, do curso de Ciência da Computação da Universidade Estadual do Ceará.
O EstudaAI é um sistema de planejamento e gerenciamento de estudos pessoal. ele permite a geração de resumos, lembretes e planos de estudos com ajuda de um LLM.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Node.js** (versão 18 ou superior)
- **npm** (geralmente vem com Node.js)
- **Python 3.13** (para o AI-Service)
- **Git** (para clonar o repositório)

## 🚀 Instalação e Configuração

### 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Instalar Dependências do Projeto Principal

```bash
npm install
```

### 3. Configurar o Frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Configurar o Backend

```bash
cd backend
npm install
npx prisma generate
```

#### Variáveis de Ambiente do Backend

Crie um arquivo `.env` na pasta `backend` com as seguintes variáveis:

```env
DATABASE_URL="sua_database_url_aqui"
SUPABASE_URL="seu_supabase_url_aqui"
ACCESS_TOKEN_SECRET="seu_secret_jwt_aqui"
SUPABASE_SERVICE_ROLE_KEY="sua_service_role_key_aqui"
```

> **Nota:** Substitua os valores entre aspas pelas suas credenciais reais.

### 5. Configurar o AI-Service

```bash
cd ai-service
```

#### Criar Ambiente Virtual Python

No **Windows**:
```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
```

No **Linux/Mac**:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

#### Instalar Dependências Python

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

#### Variáveis de Ambiente do AI-Service

Crie um arquivo `.env` na pasta `ai-service` com as seguintes variáveis:

```env
API_KEY="sua_chave_api_do_gemini_aqui"
SUPABASE_URL="seu_supabase_url_aqui"
DATABASE_URL="sua_database_url_aqui"
SUPABASE_SERVICE_ROLE_KEY="sua_service_role_key_aqui"
```

> **Nota:** Substitua os valores entre aspas pelas suas credenciais reais.

#### Desativar o Ambiente Virtual (quando necessário)

```bash
deactivate
```

Volte para a pasta raiz:
```bash
cd ../..
```

## 🏃‍♂️ Executando o Projeto

Você pode iniciar todos os serviços simultaneamente a partir da pasta raiz:

```bash
npm run start
```

Isso iniciará:
- **Frontend** na porta 3000 (ou outra configurada)
- **Backend** na porta 5000 (ou outra configurada)
- **AI-Service** na porta 8000 (ou outra configurada)

### Executando Serviços Individualmente

#### Frontend
```bash
cd frontend
npm start
```

#### Backend
```bash
cd backend
npm start
```

#### AI-Service
```bash
cd ai-service
# Ative o ambiente virtual primeiro (se não estiver ativo)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
python app.py  # ou o comando apropriado
```

## 🌐 Acessando a Aplicação

Após iniciar todos os serviços:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **AI-Service API:** http://localhost:8000

## 📁 Estrutura do Projeto

```
.
├── backend/          # API em Node.js
├── frontend/         # Aplicação React
├── ai-service/       # Serviço de IA em Python
├── package.json      # Dependências principais
└── README.md         # Este arquivo
```

## 🔧 Solução de Problemas

### Problemas Comuns

1. **Erro de porta já em uso:** 
   - Verifique se não há outros processos usando as portas 3000, 5000 ou 8000
   - Use `netstat -ano | findstr :<porta>` (Windows) ou `lsof -i :<porta>` (Linux/Mac) para identificar processos

2. **Erros de dependência:**
   - Delete as pastas `node_modules` e `package-lock.json` e execute `npm install` novamente
   - Para Python, tente atualizar o pip: `pip install --upgrade pip`

3. **Problemas com Prisma:**
   - Execute `npx prisma generate` novamente na pasta backend
   - Verifique se o DATABASE_URL está correto

### Verificando se os Serviços Estão Rodando

- Frontend: Acesse http://localhost:3000
- Backend: Acesse http://localhost:5000/health (ou endpoint similar)
- AI-Service: Acesse http://localhost:8000/docs (se usar FastAPI) ou endpoint de health check

## 📝 Notas Adicionais

- Certifique-se de que todas as URLs e chaves de API estão corretamente configuradas
- Para desenvolvimento, você pode precisar configurar CORS nos serviços backend
- O AI-Service requer uma chave de API válida do Gemini (Google AI)

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ pela equipe do projeto**
