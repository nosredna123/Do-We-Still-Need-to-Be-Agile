# Testing State - RevisAI

Este documento descreve a estratégia e o estado atual dos testes no projeto.

## Current Status
- **Automated Tests**: Nenhum framework de teste (Jest, Vitest, Cypress) está configurado no momento.
- **Test Scripts**: O `package.json` contém apenas o placeholder padrão `"test": "echo \"Error: no test specified\""`.

## Testing Strategy

### 1. Manual Testing
- **Frontend**: Verificação visual de componentes, responsividade e fluxo de chat no navegador via Vite dev server.
- **Backend**: Testes de API realizados via ferramentas como Postman ou Insomnia nos endpoints `/api/generate-flashcards` e `/api/flashcards/:userId`.

### 2. Prototyping & Mocks
- O projeto utiliza uma função `mockAIResponse` em `Dashboard.jsx` para simular o comportamento da IA durante o desenvolvimento do frontend, permitindo testar a interface e o parser de Markdown sem chamadas reais de API.

## Identified Gaps
- Falta de testes unitários para a lógica crítica de parsing no frontend.
- Falta de testes de integração para os provedores de IA no backend.
- Necessidade de testes de ponta a ponta (E2E) para o fluxo de autenticação e salvamento de cards.

## Recommended Next Steps
1. Instalar e configurar **Vitest** para testes unitários no frontend.
2. Implementar testes para a função `parseFlashcards`.
3. Adicionar **Supertest** no backend para validar as rotas do Express.

---
*Last updated: 2026-05-11*
