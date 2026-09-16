# Project Structure - RevisAI

O repositório é organizado em um monorepo simples com pastas dedicadas para backend e frontend.

## Root Directory
- `back-end/`: Código do servidor Node.js.
- `front-end/`: Código da aplicação React.
- `documentações/`: Arquivos de documentação técnica e de negócio.
- `.planning/`: Documentação de planejamento GSD (este diretório).

## Backend Structure (`/back-end`)
- `server.js`: Ponto de entrada da API e definição de rotas.
- `aiProvider.js`: Lógica de integração e abstração de provedores de IA.
- `firebaseAdmin.js`: Configuração do SDK Admin do Firebase.
- `firebase.js`: Configurações adicionais do Firebase.

## Frontend Structure (`/front-end`)
- `src/`: Código fonte principal.
    - `pages/`: Componentes de página (rotas principais).
        - `Home.jsx`: Landing page.
        - `Dashboard.jsx`: Interface principal de geração e visualização de flashcards.
        - `Login.jsx`: Fluxo de autenticação.
    - `components/`: Componentes de UI reutilizáveis (Navbar, Footer, Hero, etc.).
    - `assets/`: Recursos estáticos como imagens e SVGs.
    - `main.jsx`: Ponto de entrada do React.
    - `App.jsx`: Componente raiz com roteamento.
- `public/`: Arquivos estáticos servidos diretamente.
- `vite.config.js`: Configuração do build tool Vite.
- `tailwindcss.config.js`: (Embutido via @tailwindcss/vite) Configuração de estilos.

---
*Last updated: 2026-05-11*
