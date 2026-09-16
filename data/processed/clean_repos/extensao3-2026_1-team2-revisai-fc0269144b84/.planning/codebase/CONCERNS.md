# Technical Concerns - RevisAI

Este documento lista dívidas técnicas, riscos de segurança e áreas frágeis identificadas na base de código.

## Technical Debt
- **Módulo Firebase Duplicado**: Existem dois arquivos de configuração para Firebase no backend (`firebase.js` e `firebaseAdmin.js`). O `firebase.js` utiliza sintaxe de módulos ESM (`import`), enquanto o restante do backend usa CommonJS (`require`), o que pode causar erros de execução se for importado acidentalmente.
- **Configurações Vazias**: O arquivo `back-end/firebase.js` contém chaves vazias (`apiKey: ""`), sugerindo uma configuração incompleta ou migrada parcialmente para variáveis de ambiente.
- **Mock de IA no Frontend**: A lógica de geração de flashcards no frontend está mockada dentro do `Dashboard.jsx`, dificultando a troca para a API real sem refatoração.

## Fragility
- **Parsing via Regex**: A função `parseFlashcards` no frontend depende de expressões regulares estritas. Se o modelo de IA alterar levemente o formato do Markdown (ex: usar `###` em vez de `##`), o parsing falhará silenciosamente ou retornará uma lista vazia.
- **Acoplamento de UI e Lógica**: O `Dashboard.jsx` contém lógica de parsing, mocks e UI em um único arquivo de mais de 300 linhas, o que prejudica a manutenibilidade.

## Security
- **Exposição de Configurações**: Embora as chaves privadas pareçam estar em variáveis de ambiente, o arquivo `firebaseAdmin.js` expõe a estrutura do `serviceAccount`. É crucial garantir que o arquivo `.env` nunca seja commitado.
- **Validação de Entrada**: A validação no backend é básica. Seria ideal implementar um esquema de validação mais robusto (ex: Joi ou Zod) para garantir a integridade dos dados enviados ao Firestore.

## Quality Gaps
- **Ausência de Testes**: Como observado em `TESTING.md`, não há cobertura de testes para a lógica de negócio (geração e parsing de cards).
- **Consistência de Módulos**: Mistura de padrões de importação/exportação pode gerar confusão para novos desenvolvedores.

---
*Last updated: 2026-05-11*
