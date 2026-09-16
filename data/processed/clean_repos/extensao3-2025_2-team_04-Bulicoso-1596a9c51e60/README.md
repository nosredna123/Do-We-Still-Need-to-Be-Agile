# 💊 Buliçoso | Seu Assistente de Saúde Inteligente

> **Transformando o cuidado com a medicação: simples, seguro e inteligente.**

O **Buliçoso** é um assistente de saúde inteligente desenvolvido para a disciplina de Extensão 3. Nosso objetivo é resolver dois problemas críticos enfrentados por pacientes, especialmente idosos: a complexidade das bulas de medicamentos e o esquecimento de horários.

Utilizando o poder da Inteligência Artificial Generativa (**Google Gemini**) e técnicas avançadas como **RAG (Retrieval-Augmented Generation)**, o Buliçoso desmistifica a linguagem médica e automatiza a organização da rotina de saúde.

---

## 👥 Time de Desenvolvimento

Projeto desenvolvido por alunos da disciplina de Extensão 3:

*   **[Esterfane Camelo Cardoso]** - *[Frontend]*
*   **[Italo Vicente]** - *[Backend]*
*   **[Pedro Henrique Nonato]** - *[Frontend, QA]*
*   **[Samuel Valente]** - *[Frontend, UI/UX]*
*   **[Silvio Gonçalves]** - *[PO, Backend]*

---

## ✨ Funcionalidades Principais

### 1. 📖 Simplificação de Bulas (RAG Híbrido)
Esqueça as letras miúdas e termos técnicos.
*   **Como funciona:** O usuário envia o nome do medicamento (ou PDF da bula).
*   **O que faz:** O sistema utiliza uma base de dados vetorial (**ChromaDB**) para encontrar as informações relevantes e o **Google Gemini** para reescrevê-las em linguagem natural e acessível.
*   **Resultado:** Um resumo claro focando no que importa: **Para que serve**, **Como usar** e **Efeitos colaterais**.

### 2. ⏰ Agente de Lembretes (Tool-Calling)
Nunca mais esqueça uma dose.
*   **Como funciona:** O usuário diz ou digita sua prescrição de forma natural (ex: *"Tomar Dipirona de 8 em 8 horas por 3 dias"*).
*   **O que faz:** O Gemini atua como um Agente Inteligente, extrai os parâmetros temporais e aciona a API do **Google Calendar**.
*   **Resultado:** Lembretes automáticos criados na agenda do usuário, com notificações precisas.

---

## 🏗️ Arquitetura do Sistema

O projeto é dividido em dois componentes principais: um Backend robusto em Python e um Frontend moderno em React.

```mermaid
graph TD
    User[Usuário] -->|Interage| Frontend["Frontend (React + Vite)"]
    Frontend -->|Requisições HTTP| Backend["Backend (FastAPI)"]
    
    subgraph "Backend Services"
        Backend -->|Orquestração| LangChain
        LangChain -->|Geração de Texto| Gemini["Google Gemini API"]
        LangChain -->|Busca Vetorial| Chroma["ChromaDB (Vector Store)"]
        Backend -->|Agendamento| GCalendar["Google Calendar API"]
    end
    
    Chroma -->|Contexto de Bulas| Gemini
```

---

## 🛠️ Tech Stack

### Backend
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - Alta performance e fácil documentação.
*   **IA & LLM:** [Google Gemini](https://deepmind.google/technologies/gemini/) via [LangChain](https://python.langchain.com/).
*   **Banco de Dados Vetorial:** [ChromaDB](https://docs.trychroma.com/) - Para busca semântica eficiente.
*   **Integrações:** Google Calendar API (OAuth2).
*   **Gerenciamento de Dependências:** `pip` / `requirements.txt`.

### Frontend
*   **Framework:** [React](https://react.dev/) (v18).
*   **Build Tool:** [Vite](https://vitejs.dev/) - Rápido e leve.
*   **Linguagem:** [TypeScript](https://www.typescriptlang.org/) - Tipagem estática para segurança.
*   **Estilização:** CSS Modules / Tailwind (conforme implementação).

### GitOps
*   **CI:** GitHub Actions. 
*   Por questões de organização, dividimos o projeto em dois repositórios: um dedicado ao backend e outro ao frontend. Entretanto, para facilitar a integração e o controle das versões, configuramos um fluxo no GitHub Actions que sincroniza automaticamente as atualizações do frontend (https://github.com/esterfanecamelo/Bulicoso_frontEnd) com o repositório principal do projeto.
---

## 🚀 Como Executar o Projeto

### Pré-requisitos
*   **Python 3.11+**
*   **Node.js 18+**
*   **Chave de API do Google Gemini**
*   **Credenciais OAuth2 do Google** (arquivo `credentials.json` para o Calendar)

### 1. Configurações Gerais

1.  Na raiz do projeto, crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Configuração do Backend

1.  Configure as variáveis de ambiente:
    *   Copie o arquivo de exemplo e o renomeie para .env: `cp .env.example .env`
    *   Edite o `.env` com sua chave (`GOOGLE_API_KEY`).
    *   Deve ser incluido tanto no diretório `Backend/app` e `Backend/app/modules`

2.  Adicione o arquivo de credenciais:
    *   Crie o arquivo `credentials.json`, para poder se conectar ao Google Calendário.
    *   Salve-o na raiz da pasta `Backend/app`.

3.  Execute o servidor:
    ```bash
    cd Backend
    uvicorn app.main:app --reload
    ```
    *   O Backend rodará em: `http://localhost:8000`
    *   Documentação Swagger: `http://localhost:8000/docs`

### 3. Configuração do Frontend

1.  Navegue até a pasta do frontend:
    ```bash
    cd frontend
    ```

2.  Instale as dependências:
    ```bash
    npm install
    npm install react-router-dom
    ```

3.  Execute o servidor de desenvolvimento:
    ```bash
    npm run dev
    ```
    *   O Frontend rodará geralmente em: `http://localhost:5173`

---

## 📋 Requisitos do Projeto
Documentação detalhada dos requisitos funcionais e não funcionais do sistema.

*   **[Acessar Requisitos (PDF)](<Documentação/Requisitos/Requisitos - Buliçoso.pdf>)**

---

## 🧪 Plano de Testes
O projeto conta com uma documentação dedicada à garantia de qualidade (QA), detalhando as estratégias e casos de teste.

*   **[Acessar Plano de Testes (PDF)](<Documentação/Plano_de_Testes/Plano de Testes do Buliçoso.docx.pdf>)**

---

## 📁 Estrutura de Pastas

```
Extensao-3/
├── Backend/                # API e Lógica de IA
│   ├── app/
│   │   ├── api/            # Endpoints (Rotas)
│   │   ├── core/           # Configurações
│   │   ├── db/             # Configurações de Banco de Dados
│   │   ├── modules/        # Módulos Principais (RAG, Calendar)
│   │   ├── services/       # Lógica de Negócio
│   │   └── ...
│   └── requirements.txt
├── frontend/               # Interface do Usuário
│   ├── src/
│   ├── package.json
│   └── ...
├── Documentação/           # Documentação do Projeto
│   ├── vivências/          # Relatórios de experiências (Sprints)
│   ├── Plano_de_Testes/    # Planejamento e Casos de Teste
│   └── Requisitos/         # Requisitos do Projeto
└── README.md               # Documentação Principal

> **Nota:** O diretório `vivências` contém os relatórios das experiências vivenciadas pelo time em cada sprint.
```

## 🤝 Contribuição

Este é um projeto acadêmico open-source. Sinta-se à vontade para abrir Issues ou Pull Requests para melhorias.

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.