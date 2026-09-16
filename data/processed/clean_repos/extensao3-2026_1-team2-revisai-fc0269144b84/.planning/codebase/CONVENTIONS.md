# Coding Conventions - RevisAI

Este documento define os padrões de código e convenções utilizados no projeto.

## General Standards
- **Language**: JavaScript (ESM no frontend, CommonJS no backend).
- **Naming**: 
    - `PascalCase` para componentes React e classes.
    - `camelCase` para variáveis, funções e instâncias.
    - `UPPER_SNAKE_CASE` para constantes globais.
- **Formatting**: Indentação de 2 espaços.

## Frontend (React)
- **Components**: Componentes funcionais com Hooks.
- **Hooks**: Uso extensivo de `useState`, `useEffect` e `useRef` para gerenciamento de estado e DOM.
- **Styling**: Utility-first com Tailwind CSS.
- **Animations**: GSAP para transições e micro-interações premium.
- **Icons**: Componentes Lucide React ou SVGs inline para controle total de estilo.

## Backend (Express)
- **Structure**: Rotas definidas no `server.js` com lógica de suporte em módulos separados.
- **Abstractions**: Uso de classes para provedores de serviços (ex: `AIProvider`).
- **Middleware**: Uso de `cors` e `express.json()`.

## Error Handling Pattern
- **Backend**: 
    - Uso de blocos `try/catch` em todas as rotas assíncronas.
    - Retorno de status `400` para erros de validação e `500` para erros internos.
    - Middleware de erro global para capturar exceções não tratadas.
- **Frontend**:
    - Validação de entrada simples (ex: `input.trim()`).
    - Feedback visual via Toasts/Notificações para ações do usuário.

## AI Interaction
- O sistema utiliza um parser customizado para extrair dados de respostas em Markdown da IA, seguindo o padrão:
  ```markdown
  *Pergunta:* [Texto]
  *Resposta:* [Texto]
  ```

---
*Last updated: 2026-05-11*
