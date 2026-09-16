# Architecture - RevisAI

O RevisAI segue um padrão de arquitetura **Client-Server** desacoplado, com o frontend consumindo uma API REST no backend.

## System Overview
- **Frontend**: Uma Single Page Application (SPA) construída com React e Vite, focada em uma interface de usuário rica e performática (usando GSAP e Tailwind).
- **Backend**: Um servidor Node.js/Express que atua como um orquestrador entre o usuário, os serviços de IA e o banco de dados.

## Key Components & Layers

### 1. Frontend Layer (React)
- **Routing**: Gerenciado pelo `react-router-dom`.
- **State Management**: Baseado em Hooks do React (`useState`, `useEffect`).
- **Pages**: Localizadas em `src/pages/`, representam as visualizações principais (Dashboard, Home, Login).
- **Components**: Componentes reutilizáveis em `src/components/` (Navbar, Hero, etc.).

### 2. Backend Layer (Express)
- **API Routes**: Definidas em `server.js`, gerenciam as requisições de geração e consulta de flashcards.
- **AI Abstraction**: O `aiProvider.js` implementa um padrão **Factory/Interface**, permitindo que o provedor de IA (OpenAI, AWS) seja trocado via configuração (`.env`) sem alterar a lógica de negócio.
- **Persistence**: Integração direta com Firebase Firestore via `firebase-admin`.

## Data Flow
1. O usuário insere um tema/prompt no **Dashboard**.
2. O **Frontend** envia uma requisição `POST` para o **Backend**.
3. O **Backend** inicializa o `AIProvider` configurado.
4. O `AIProvider` solicita a geração dos flashcards ao serviço de LLM (ex: OpenAI).
5. O **Backend** recebe a resposta JSON, valida a estrutura e salva no **Firestore**.
6. O **Backend** retorna os dados para o **Frontend**, que atualiza a interface.

---
*Last updated: 2026-05-11*
