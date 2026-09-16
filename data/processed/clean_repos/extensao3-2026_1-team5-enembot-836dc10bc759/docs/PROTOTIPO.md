# ENEMBot - Prototipo funcional

Branch: `feat/prototipo-chatbot`

Este prototipo entrega o fluxo ponta-a-ponta do chatbot ENEM com respostas
**mockadas** (sem LLM real). O objetivo e validar UX, estrutura de pastas e a
arquitetura de troca do adapter de IA.

## Como rodar

1. **Frontend (Next.js 15 + React 19)**
   ```bash
   # na raiz do repo
   npm install
   cp frontend/.env.local.example frontend/.env.local   # e preencher
   npm run dev
   ```
   Abre em `http://localhost:3000`.

2. **Backend (FastAPI)** - opcional nesta fase, UI nao depende dele.
   ```bash
   cd backend
   uv sync
   uv run uvicorn main:app --reload
   ```

3. **Supabase** - ja linkado (`supabase/config.toml`). Migrations em
   `supabase/migrations/` sao aplicadas com:
   ```bash
   SUPABASE_DB_PASSWORD=... supabase db push
   ```

## Fluxo do usuario

1. Home (`/`) apresenta **builds** (Estrategista / Teorico / Sniper) e
   **disciplinas** (Matematica, Linguagens, Natureza, Humanas, Redacao).
2. Usuario escolhe uma build (URL-synced) e clica numa materia.
3. Navega para `/chat/[subjectId]?build=...`.
4. O bot saudacao + entrega a primeira questao.
5. Usuario marca alternativa -> feedback imediato com explicacao.
6. Usuario digita `"proxima"` ou pergunta livre -> bot adapta.

## Arquitetura

### Camada de dominio (frontend/app/lib)

| Arquivo | Papel |
|---|---|
| `types.ts` | Tipos da UI (Build, Subject, Question, ChatMessage) |
| `catalog.ts` | Builds e disciplinas |
| `questionBank.ts` | 9 questoes ENEM mockadas; `pickQuestion()` respeita build |
| `supabaseClient.ts` | Client tipado do Supabase (singleton) |
| `database.types.ts` | Tipos gerados por `supabase gen types` |
| `llm/llmClient.ts` | **Contrato** `LlmClient` (start/answer/next/freeReply) |
| `llm/mockLlmClient.ts` | Implementacao mock com delay simulado |
| `llm/index.ts` | Facade - **unico ponto de troca** para OpenAI |

### Para plugar OpenAI futuramente

Criar `frontend/app/lib/llm/openAiLlmClient.ts` implementando `LlmClient` e
alterar uma linha em `llm/index.ts`:

```ts
export const llm: LlmClient = openAiLlmClient; // era mockLlmClient
```

A UI nao precisa ser tocada.

## Banco de dados (Supabase)

Projeto ref: `kkmfnutncpiesqouaipw`.

Migrations aplicadas:
- `20260416221329_init_schema_enembot.sql`
- `20260416221455_seed_catalogo.sql`

### Adaptacoes vs. `criarDB_V4.sql`

- `AUTO_INCREMENT` -> `BIGSERIAL`
- `YEAR` -> `SMALLINT` com CHECK
- `CamelCase` -> `snake_case` (convencao PostgREST / Supabase)
- Timestamps `created_at` / `updated_at` (TIMESTAMPTZ) com trigger de auto-update
- Indices em todas as FKs
- RLS habilitada em todas as tabelas com policies tolerantes para prototipo

### Acrescimos propostos

- **`chat_session`** e **`chat_message`** - essenciais para o produto: uma sessao
  de estudo e suas mensagens (user/assistant/system) referenciando questao e
  resposta quando aplicavel.
- **`questao.origem`** (`oficial` | `gerada_ia`) - rastrear questoes geradas pela
  IA vs. oficiais.
- **`questao.dificuldade`** (`facil` | `media` | `dificil`) - o build "sniper"
  usa esse filtro.
- **`questao.fonte_prompt`** - prompt usado quando a questao foi gerada pela IA.
- **`aluno.auth_user_id`** - integracao com Supabase Auth preservando a coluna
  `senha` legada para compatibilidade.
- **`disciplina.cor_hex`** / **`disciplina.icone`** - feed da UI direto do banco.
- **`log.payload jsonb`** - logs estruturados.

## Mock LLM

`mockLlmClient.ts` simula:
- **startSession**: greeting contextual por build + primeira questao
- **answerQuestion**: confere letra, retorna feedback (Teorico = explicacao mais
  longa, demais = curta)
- **nextQuestion**: proxima questao nao repetida, respeitando filtro de
  dificuldade do build
- **freeReply**: responde a palavras-chave como "dica", "nao entendi",
  "proxima", "pausa"

Todas chamadas tem delay ~300-450ms para simular latencia real.

## Pendencias / Proximos passos

- [ ] Integrar Supabase Auth no frontend (email + magic link)
- [ ] Persistir `chat_session` e `chat_message` de verdade (hoje e so estado
      local)
- [ ] Implementar `openAiLlmClient.ts` e gate por env `OPENAI_API_KEY`
- [ ] Importar banco oficial de questoes ENEM (hoje sao 9 mockadas)
- [ ] Melhorar acessibilidade (roving tabindex na sidebar, live regions)
- [ ] Testes: Playwright e2e, Vitest para `pickQuestion` e `mockLlmClient`
- [ ] Telemetria simples via `log` table para entender onde o aluno desiste
