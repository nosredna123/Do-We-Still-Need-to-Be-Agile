-- =============================================================================
-- ENEMBot - Schema inicial (adaptado de criarDB_V4.sql para PostgreSQL/Supabase)
-- =============================================================================
-- Decisoes de adaptacao vs. schema original do grupo:
--   * AUTO_INCREMENT -> BIGSERIAL
--   * YEAR           -> SMALLINT (com CHECK de range)
--   * BOOLEAN status -> mantido, com DEFAULT TRUE
--   * snake_case     -> adotado para conformidade com PostgREST/Supabase
--   * Timestamps     -> TIMESTAMPTZ com DEFAULT NOW() em created_at/updated_at
--   * RLS            -> habilitado em todas as tabelas (policies tolerantes
--                       para prototipo; revisar para producao)
--
-- Acrescimos propostos (justificativa no relatorio da task):
--   * tabela chat_session  - uma sessao de estudo do aluno com o chatbot
--   * tabela chat_message  - mensagens trocadas (user|assistant|system)
--   * coluna dificuldade em questao
--   * coluna origem em questao ('oficial' | 'gerada_ia')
--   * coluna fonte_prompt em questao (o prompt usado pela IA, quando aplicavel)
-- =============================================================================

-- --- Dominios/tipos -----------------------------------------------------------

create type public.questao_origem as enum ('oficial', 'gerada_ia');
create type public.questao_dificuldade as enum ('facil', 'media', 'dificil');
create type public.chat_role as enum ('user', 'assistant', 'system');

-- --- Tabelas base -------------------------------------------------------------

create table public.instituicao (
  id_instituicao bigserial primary key,
  nome varchar(255) not null,
  sigla varchar(20),
  status boolean not null default true,
  uf char(2),
  created_at timestamptz not null default now()
);

create table public.banca (
  id_banca bigserial primary key,
  nome varchar(255) not null unique,
  sigla varchar(20),
  created_at timestamptz not null default now()
);

create table public.aluno (
  id_aluno bigserial primary key,
  email varchar(255) not null unique,
  nome varchar(255) not null,
  id_instituicao bigint references public.instituicao(id_instituicao) on delete set null,
  -- Auth delegada ao Supabase Auth via auth_user_id. Senha legacy opcional.
  auth_user_id uuid unique,
  senha varchar(255),
  avatar_url varchar(255),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.prova (
  id_prova bigserial primary key,
  nome varchar(255) not null,
  data_prova date,
  id_aluno bigint references public.aluno(id_aluno) on delete set null,
  status boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.disciplina (
  id_disciplina bigserial primary key,
  nome varchar(255) not null unique,
  cor_hex varchar(7),
  icone varchar(50),
  created_at timestamptz not null default now()
);

create table public.assunto (
  id_assunto bigserial primary key,
  nome varchar(255) not null,
  id_disciplina bigint not null references public.disciplina(id_disciplina) on delete cascade,
  id_assunto_pai bigint references public.assunto(id_assunto) on delete set null,
  created_at timestamptz not null default now()
);
create index idx_assunto_disciplina on public.assunto(id_disciplina);
create index idx_assunto_pai on public.assunto(id_assunto_pai);

create table public.questao (
  id_questao bigserial primary key,
  id_prova bigint references public.prova(id_prova) on delete set null,
  enunciado text not null,
  tipo varchar(20),
  comentario text,
  status boolean not null default true,
  id_banca bigint references public.banca(id_banca) on delete set null,
  ano smallint check (ano is null or (ano between 1900 and 2100)),
  verificada boolean not null default false,
  -- Acrescimos do prototipo
  origem public.questao_origem not null default 'oficial',
  dificuldade public.questao_dificuldade,
  fonte_prompt text,
  created_at timestamptz not null default now()
);
create index idx_questao_banca on public.questao(id_banca);
create index idx_questao_ano on public.questao(ano);
create index idx_questao_origem on public.questao(origem);

create table public.questao_assunto (
  id_questao bigint not null references public.questao(id_questao) on delete cascade,
  id_assunto bigint not null references public.assunto(id_assunto) on delete cascade,
  primary key (id_questao, id_assunto)
);
create index idx_questao_assunto_assunto on public.questao_assunto(id_assunto);

create table public.alternativa (
  id_questao bigint not null references public.questao(id_questao) on delete cascade,
  letra char(1) not null check (letra in ('A','B','C','D','E')),
  correta boolean not null default false,
  texto text not null,
  feedback text,
  primary key (id_questao, letra)
);

create table public.resposta (
  id_resposta bigserial primary key,
  id_aluno bigint not null references public.aluno(id_aluno) on delete cascade,
  id_questao bigint not null references public.questao(id_questao) on delete cascade,
  texto_resposta text,
  letra_resposta char(1) check (letra_resposta is null or letra_resposta in ('A','B','C','D','E')),
  correta boolean,
  data_resposta timestamptz not null default now()
);
create index idx_resposta_aluno on public.resposta(id_aluno);
create index idx_resposta_questao on public.resposta(id_questao);

create table public.log (
  id_log bigserial primary key,
  acao varchar(255) not null,
  id_aluno bigint references public.aluno(id_aluno) on delete set null,
  payload jsonb,
  data_hora timestamptz not null default now()
);
create index idx_log_aluno on public.log(id_aluno);

create table public.comentarios (
  id_comentario bigserial primary key,
  id_questao bigint not null references public.questao(id_questao) on delete cascade,
  id_aluno bigint not null references public.aluno(id_aluno) on delete cascade,
  comentario_pai_id bigint references public.comentarios(id_comentario) on delete cascade,
  texto text not null,
  data_comentario timestamptz not null default now(),
  status boolean not null default true
);
create index idx_comentario_questao on public.comentarios(id_questao);

create table public.tags (
  id_tag bigserial primary key,
  nome varchar(50) not null unique,
  descricao varchar(255),
  cor_hex varchar(7),
  icone varchar(50)
);

create table public.aluno_questao_tags (
  id_aluno bigint not null references public.aluno(id_aluno) on delete cascade,
  id_questao bigint not null references public.questao(id_questao) on delete cascade,
  id_tag bigint not null references public.tags(id_tag) on delete cascade,
  data_tag timestamptz not null default now(),
  primary key (id_aluno, id_questao, id_tag)
);

-- --- Chat (acrescimo do prototipo) -------------------------------------------

create table public.chat_session (
  id_chat bigserial primary key,
  id_aluno bigint not null references public.aluno(id_aluno) on delete cascade,
  id_disciplina bigint references public.disciplina(id_disciplina) on delete set null,
  build varchar(30),                           -- 'estrategista' | 'teorico' | 'sniper'
  titulo varchar(255),
  status boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index idx_chat_aluno on public.chat_session(id_aluno);

create table public.chat_message (
  id_mensagem bigserial primary key,
  id_chat bigint not null references public.chat_session(id_chat) on delete cascade,
  role public.chat_role not null,
  conteudo text not null,
  id_questao bigint references public.questao(id_questao) on delete set null,
  id_resposta bigint references public.resposta(id_resposta) on delete set null,
  metadata jsonb,
  created_at timestamptz not null default now()
);
create index idx_chat_message_chat on public.chat_message(id_chat);

-- --- Trigger utilitario de updated_at ----------------------------------------

create or replace function public.tg_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger tg_aluno_updated_at
  before update on public.aluno
  for each row execute function public.tg_set_updated_at();

create trigger tg_chat_session_updated_at
  before update on public.chat_session
  for each row execute function public.tg_set_updated_at();

-- --- RLS ---------------------------------------------------------------------
-- Policies tolerantes para prototipo: leitura publica em dados de catalogo,
-- escrita bloqueada por padrao. Tabelas de aluno exigem autenticacao.
-- Revisar antes de producao.

alter table public.instituicao enable row level security;
alter table public.banca enable row level security;
alter table public.disciplina enable row level security;
alter table public.assunto enable row level security;
alter table public.prova enable row level security;
alter table public.questao enable row level security;
alter table public.questao_assunto enable row level security;
alter table public.alternativa enable row level security;
alter table public.tags enable row level security;
alter table public.aluno enable row level security;
alter table public.resposta enable row level security;
alter table public.log enable row level security;
alter table public.comentarios enable row level security;
alter table public.aluno_questao_tags enable row level security;
alter table public.chat_session enable row level security;
alter table public.chat_message enable row level security;

-- Catalogo publico (read-only para anon)
create policy "catalogo_read" on public.instituicao for select using (true);
create policy "catalogo_read" on public.banca for select using (true);
create policy "catalogo_read" on public.disciplina for select using (true);
create policy "catalogo_read" on public.assunto for select using (true);
create policy "catalogo_read" on public.tags for select using (true);
create policy "catalogo_read" on public.questao for select using (true);
create policy "catalogo_read" on public.questao_assunto for select using (true);
create policy "catalogo_read" on public.alternativa for select using (true);
create policy "catalogo_read" on public.prova for select using (true);

-- Tabelas do aluno: acesso apenas do proprio aluno autenticado
create policy "aluno_self_read" on public.aluno
  for select using (auth.uid() = auth_user_id);
create policy "aluno_self_update" on public.aluno
  for update using (auth.uid() = auth_user_id);

create policy "resposta_self" on public.resposta
  for all using (
    id_aluno in (select id_aluno from public.aluno where auth_user_id = auth.uid())
  );

create policy "comentarios_read_all" on public.comentarios
  for select using (status = true);
create policy "comentarios_self_write" on public.comentarios
  for all using (
    id_aluno in (select id_aluno from public.aluno where auth_user_id = auth.uid())
  );

create policy "tags_pessoais_self" on public.aluno_questao_tags
  for all using (
    id_aluno in (select id_aluno from public.aluno where auth_user_id = auth.uid())
  );

create policy "chat_session_self" on public.chat_session
  for all using (
    id_aluno in (select id_aluno from public.aluno where auth_user_id = auth.uid())
  );

create policy "chat_message_self" on public.chat_message
  for all using (
    id_chat in (
      select cs.id_chat from public.chat_session cs
      join public.aluno a on a.id_aluno = cs.id_aluno
      where a.auth_user_id = auth.uid()
    )
  );

create policy "log_self_read" on public.log
  for select using (
    id_aluno in (select id_aluno from public.aluno where auth_user_id = auth.uid())
  );
