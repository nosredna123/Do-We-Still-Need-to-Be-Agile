# Plano de implementação: novas análises de robustez, trajetórias avaliativas e triangulação

## Objetivo

Este plano organiza uma nova leva de agregações, estratificações e visualizações
para fortalecer a narrativa do `paper_v9` usando somente dados já disponíveis.
O foco é transformar limitações atualmente descritas em `Threats to Validity`
em análises de robustez, triangulação ou achados descritivos adicionais, sem
ultrapassar os limites observacionais do estudo.

Escopo acordado:

- Implementação incremental com scripts, dados derivados, figuras, metadados e
  testes por fase.
- Cobertura de todas as oportunidades identificadas, mas priorizadas por
  melhor relação custo-complexidade/benefício.
- Inclusão de tarefas de integração posterior no texto LaTeX do artigo.

## Princípios metodológicos

- [ ] Manter todas as inferências como descritivas/exploratórias.
- [ ] Preservar o grão analítico de cada fonte de dados.
- [ ] Não transformar ausência de evidência em pontuação baixa.
- [ ] Não imputar M6b quando não houver T1 commit subjects.
- [ ] Não tratar M1/M2 como telemetria objetiva de uso de IA.
- [ ] Não tratar M8 como defeito semântico.
- [ ] Não tratar M5 como diagnóstico direto de fricção.
- [ ] Usar visualizações com pontos por equipe-semestre sempre que possível.
- [ ] Registrar metadados, cobertura, limitações e checksums para cada novo
  artefato.
- [ ] Registrar cada novo artefato analítico/visual em um catálogo versionado
  de uso editorial, com utilidade, limitações, melhor contexto de uso e status
  de adoção no artigo.
- [ ] Tratar o catálogo como fonte editorial integrada: decisões de revisão
  textual devem considerar tanto as entradas de artefatos quanto o
  `Registro de respostas aos insights esperados`.
- [ ] Atualizar o catálogo de uso sempre que uma figura/dado for promovido ao
  texto principal, movido ao apêndice, substituído, descartado ou usado para
  responder a uma crítica específica.
- [ ] Seguir o protocolo operacional por demanda/artefato antes de gerar novas
  figuras: consultar o catálogo, decidir se artefato existente atende, pedir
  confirmação quando houver mudança de escopo ou integração textual, gerar,
  validar, catalogar e só então propor inserção editorial.
- [ ] Criar testes focados para cada novo script de resultados.

## Convenções propostas

### Localização dos scripts

Novos scripts de resultados devem ficar em:

```text
paper_v9/scripts/results/
```

### Localização dos artefatos

Novos CSVs, PNGs, SVGs, PDFs e metadados devem ficar em:

```text
paper_v9/figures/
```

### Localização dos testes

Novos testes devem ficar em:

```text
paper_v9/tests/
```

### Prefixos recomendados

Usar prefixos consistentes por família analítica:

```text
rq2_score_trajectory_*
rq2_planning_concentration_*
rq2_operational_regularity_*
rq3_complexity_confounding_*
rq3_influence_map_*
rq2_m5_2025_triangulation_*
```

### Catálogo versionado de artefatos

Toda nova família de dados/figuras deve atualizar um controle versionado:

```text
paper_v9/ARTIFACT_USAGE_CATALOG.md
```

O catálogo deve funcionar como índice editorial e analítico. Seu objetivo é
evitar que cada nova decisão de escrita exija reabrir e reavaliar todos os
artefatos gerados. Ele deve resumir, em linguagem curta, para que cada artefato
serve, onde ele é forte, onde ele é fraco, qual é seu status no paper e quais
insights esperados já foram empiricamente respondidos.

Campos mínimos por artefato ou família de artefatos:

| Campo | Descrição |
|---|---|
| `artifact_id` | Identificador estável, preferencialmente igual ao stem do arquivo |
| `artifact_family` | Família analítica, por exemplo `student_syndrome`, `score_trajectory`, `complexity` |
| `files` | Links relativos para PNG/SVG/PDF/CSV/metadata |
| `data_inputs` | Principais inputs usados |
| `unit_of_analysis` | Grão analítico explícito |
| `main_question` | Pergunta que o artefato ajuda a responder |
| `best_use` | Melhor local de uso: Results, Discussion, Threats, appendix, response letter |
| `key_reading` | Leitura curta dos padrões observados |
| `utility_score` | Alta, média ou baixa utilidade editorial |
| `limitations` | Limitações específicas daquele artefato |
| `status` | `candidate`, `main_text`, `appendix`, `diagnostic_only`, `superseded`, `discarded` |
| `superseded_by` | Artefato substituto, quando aplicável |
| `last_reviewed` | Data da última avaliação editorial |

Esse catálogo deve ser atualizado junto com cada fase e revisado antes da
integração no LaTeX. Em fases ou tarefas de revisão editorial, o catálogo deve
ser lido como um todo: entradas de artefatos, status, limitações, artefatos
substituídos/descartados e o `Registro de respostas aos insights esperados`
devem informar conjuntamente a decisão de inserir, mover, condensar ou omitir
material no artigo.

## Protocolo operacional obrigatório por demanda/artefato

Este protocolo deve ser seguido para toda nova demanda analítica, nova figura,
nova tabela ou novo dado derivado. A geração do artefato é apenas uma etapa; o
fluxo completo inclui consulta prévia ao catálogo, decisão de reaproveitamento
ou criação, validação, catalogação e eventual integração textual.

### Etapa 1 — Formular a demanda analítica

Antes de implementar qualquer script ou figura, registrar claramente:

- [ ] Qual pergunta narrativa/metodológica está sendo respondida?
- [ ] Qual ameaça de validade, seção do artigo ou lacuna interpretativa está
  sendo abordada?
- [ ] Qual é o grão analítico esperado?
- [ ] Quais dados existentes são necessários?
- [ ] Que tipo de saída seria útil: figura, tabela, CSV, nota editorial ou
  apenas diagnóstico interno?

**Output esperado**

- Uma frase curta do tipo:

```text
Demanda: avaliar se concentração final de atividade se associa a delta de score,
estratificada por planejamento visível em T1.
```

### Etapa 2 — Consultar o catálogo antes de criar algo novo

Antes de gerar novo artefato, consultar:

```text
paper_v9/ARTIFACT_USAGE_CATALOG.md
```

Perguntas obrigatórias:

- [ ] Já existe artefato que responda à demanda?
- [ ] Existe artefato parcialmente adequado que poderia ser reutilizado?
- [ ] Existe artefato marcado como `superseded` que não deve ser reutilizado?
- [ ] Existe artefato `diagnostic_only` que explica por que uma abordagem foi
  descartada?
- [ ] O catálogo indica alguma limitação ou risco de má interpretação relevante?

**Decisão possível**

| Situação | Ação |
|---|---|
| Artefato existente atende plenamente | Não gerar novo artefato; usar e atualizar status/uso no catálogo |
| Artefato existente atende parcialmente | Propor adaptação ou nova versão derivada |
| Artefato existente foi substituído | Usar `superseded_by` |
| Nenhum artefato atende | Criar novo artefato seguindo as etapas abaixo |

### Gate de autorização A — Reuso vs. novo artefato

Pedir confirmação do usuário quando:

- [ ] houver mais de uma opção razoável de artefato existente;
- [ ] a demanda puder ser respondida sem nova geração, mas com interpretação de
  artefato já existente;
- [ ] a criação de novo artefato exigir mudança de escopo, nova heurística ou
  nova classificação;
- [ ] a nova visualização puder competir/substituir figura já candidata ao texto.

Não é necessário pedir confirmação quando:

- [ ] a tarefa já pede explicitamente a criação de novo artefato específico;
- [ ] não existe artefato catalogado que responda à demanda;
- [ ] a mudança é apenas correção técnica ou regeneração de artefato já aprovado.

### Etapa 3 — Especificar contrato do novo artefato

Antes da implementação, documentar no plano da tarefa:

- [ ] inputs exatos;
- [ ] outputs esperados;
- [ ] unidade de análise;
- [ ] denominadores;
- [ ] estratos/grupos;
- [ ] métrica principal;
- [ ] limitação principal;
- [ ] critério de sucesso visual/analítico;
- [ ] teste focado a criar/atualizar.

**Output esperado**

Um bloco curto no issue/plano/sessão, por exemplo:

```text
Artefato proposto: rq2_score_delta_vs_final7_commit_concentration.
Input: evaluator_team_cuts, M6a, final7 concentration.
Unidade: team-semester.
Output: scatter PNG/SVG/PDF, data CSV, metadata JSON.
Critério: 14 team-semesters, final7_share_pct em [0,100], delta score numérico.
```

### Gate de autorização B — Heurísticas e classificações novas

Pedir confirmação do usuário antes de implementar quando a tarefa exigir:

- [ ] novo threshold substantivo;
- [ ] nova classificação de equipes;
- [ ] nova taxonomia de trajetória;
- [ ] agregação que possa alterar a interpretação do artigo;
- [ ] descarte/exclusão de casos;
- [ ] mudança de figura principal candidata.

Exemplos:

- threshold para `improved/stable/declined`;
- divisão alta/baixa complexidade;
- definição de regularity index;
- classificação manual de tipo de integração GenAI.

### Etapa 4 — Implementar geração reprodutível

Para cada novo artefato:

- [ ] criar ou atualizar script em `paper_v9/scripts/results/`;
- [ ] gerar CSV de dados usados pela figura;
- [ ] gerar CSV de resumo, quando aplicável;
- [ ] gerar PNG/SVG/PDF;
- [ ] gerar `.metadata.json`;
- [ ] incluir checksums/config no metadata;
- [ ] incluir limitações no metadata;
- [ ] imprimir resumo de cobertura ao final do script.

### Etapa 5 — Validar tecnicamente

Validação mínima:

- [ ] `py_compile` do script;
- [ ] teste focado com `pytest`;
- [ ] checagem de existência dos outputs;
- [ ] checagem de ranges esperados;
- [ ] checagem de denominadores (`n`);
- [ ] inspeção visual da figura PNG;
- [ ] leitura breve do CSV/summary para confirmar valores plausíveis.

Comando padrão:

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m py_compile <script.py> <test.py>
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m pytest <test.py>
```

### Etapa 6 — Atualizar o catálogo imediatamente

Depois da validação técnica, atualizar:

```text
paper_v9/ARTIFACT_USAGE_CATALOG.md
```

Cada novo artefato deve registrar:

- [ ] `artifact_id`;
- [ ] arquivos gerados;
- [ ] inputs;
- [ ] unidade de análise;
- [ ] pergunta principal;
- [ ] melhor uso;
- [ ] leitura principal;
- [ ] limitações;
- [ ] status inicial;
- [ ] relação com seção do artigo;
- [ ] relação com ameaça de validade, se houver;
- [ ] artefato substituído, se houver;
- [ ] `last_reviewed`.

Quando a tarefa/fase tiver um bloco **Insight esperado**, a atualização do
catálogo também deve incluir ou atualizar uma linha na seção
`Registro de respostas aos insights esperados`, com:

- [ ] texto do insight/pergunta em forma curta;
- [ ] tarefa(s) que produziram a evidência;
- [ ] artefatos de evidência usados para responder;
- [ ] resposta empírica curta, com números principais quando disponíveis;
- [ ] uso editorial sugerido;
- [ ] ressalvas para evitar leitura causal ou extrapolação indevida.

Essa resposta ao insight é parte do critério de conclusão da tarefa: não basta
gerar figura/CSV/metadados se o insight esperado já puder ser respondido pelos
artefatos gerados.

### Gate de autorização C — Promoção editorial

Pedir confirmação do usuário antes de:

- [ ] marcar artefato como `main_text`;
- [ ] mover artefato para `appendix` como decisão editorial definitiva;
- [ ] marcar artefato como `discarded`;
- [ ] marcar artefato existente como `superseded`;
- [ ] substituir figura já usada no texto;
- [ ] editar LaTeX para inserir/remover figura.

### Etapa 7 — Propor integração textual

Antes de editar o LaTeX, preparar uma proposta curta:

- [ ] seção/subseção alvo;
- [ ] subseções secundariamente afetadas pelo novo argumento;
- [ ] artefato(s) a inserir;
- [ ] tese interpretativa em uma frase;
- [ ] números principais;
- [ ] limitação local a preservar;
- [ ] impacto esperado em `Threats to Validity`;
- [ ] status proposto no catálogo.

**Output esperado**

Exemplo:

```text
Proposta: inserir rq2_score_delta_vs_final7_commit_concentration em Results/RQ2.
Tese: concentração final alta é mais frequente em equipes com menor ganho avaliativo,
especialmente quando planejamento visível é baixo. Limitação: associação descritiva,
n=14, sem causalidade.
```

### Gate de autorização D — Edição de texto do artigo

Pedir confirmação do usuário antes de editar:

- [ ] `results.tex`;
- [ ] `discussion.tex`;
- [ ] `threats_to_validity.tex`;
- [ ] `conclusion.tex`;
- [ ] captions ou labels LaTeX de figuras principais.

Exceção: correções mecânicas pós-autorização, como ajuste de label/caption
necessário para compilar, podem ser feitas sem nova pergunta se não alterarem a
interpretação.

### Etapa 8 — Planejar o refactoring editorial sistêmico

Cada artefato ou argumento novo deve ser tratado como uma pequena refatoração do
texto, não como uma inserção local isolada. Antes de editar, revisar
sistematicamente as subseções potencialmente afetadas para evitar redundância,
contradições, lacunas de transição ou claims mais fortes que os dados permitem.

Checklist obrigatório:

- [ ] consultar o catálogo completo, incluindo o `Registro de respostas aos
  insights esperados`, antes de propor alterações textuais;
- [ ] verificar se a introdução/motivação precisa antecipar a nova distinção;
- [ ] verificar se a pergunta de pesquisa relacionada precisa de ajuste de
  escopo ou wording;
- [ ] verificar se a seção de dados/métodos precisa explicar nova métrica,
  estratificação, exclusão ou normalização;
- [ ] verificar se os resultados precisam de transição para a nova figura/tabela;
- [ ] verificar se a discussão precisa reinterpretar achados anteriores à luz do
  novo artefato;
- [ ] verificar se `Threats to Validity` precisa deixar de tratar uma limitação
  como apenas ameaça e passar a descrevê-la como parcialmente mitigada;
- [ ] verificar se conclusão/implicações precisam ser suavizadas, fortalecidas
  ou qualificadas;
- [ ] verificar se captions, labels e referências cruzadas continuam coerentes;
- [ ] verificar se algum artefato anterior ficou redundante ou foi suplantado.

**Mapa editorial mínimo por artefato**

| Parte do texto | Pergunta de revisão |
|---|---|
| Introduction | O novo achado muda a promessa ou motivação do artigo? |
| Research Questions | A análise responde diretamente uma RQ existente ou sugere sub-questão? |
| Data/Methods | O leitor consegue reproduzir a métrica/estrato usado no artefato? |
| Results | O artefato tem narrativa local, números principais e transição? |
| Discussion | O novo achado muda a interpretação de padrões já discutidos? |
| Threats to Validity | A ameaça foi mitigada, deslocada ou apenas reconhecida? |
| Conclusion | O claim final continua proporcional à evidência acumulada? |
| Appendix/Supplement | O artefato deve ir ao texto principal ou apoiar robustez? |

**Output esperado**

Antes da edição, produzir uma mini-matriz:

```text
Artefato: rq2_score_delta_vs_final7_commit_concentration
Results/RQ2: inserir figura e descrever associação.
Methods: acrescentar definição de final7 concentration e delta score.
Discussion: conectar com processo contínuo vs. entrega tardia.
Threats: atualizar ameaça de student syndrome como parcialmente mitigada.
Conclusion: sem alteração.
```

### Gate de autorização E — Escopo do refactoring textual

Pedir confirmação do usuário quando a revisão sistêmica indicar que:

- [ ] mais de uma seção precisará ser editada;
- [ ] uma seção precisará mudar seu argumento central;
- [ ] um claim existente deve ser enfraquecido ou fortalecido;
- [ ] uma figura/tabela anterior deve ser removida, substituída ou deslocada;
- [ ] uma ameaça de validade deve ser reclassificada como mitigada;
- [ ] a conclusão do artigo pode mudar.

### Etapa 9 — Integrar no artigo e revalidar

Após autorização:

- [ ] editar a seção/subseção pertinente;
- [ ] aplicar o mapa editorial aprovado às demais subseções afetadas;
- [ ] atualizar captions;
- [ ] atualizar referências cruzadas;
- [ ] atualizar `Threats to Validity` se a nova análise mitigar ameaça
  previamente declarada;
- [ ] atualizar catálogo com status final;
- [ ] compilar LaTeX;
- [ ] revisar coerência local da seção.
- [ ] revisar coerência global entre Results, Discussion, Threats e Conclusion.

### Etapa 10 — Registrar decisão final

Para cada artefato implementado, encerrar com:

- [ ] status final no catálogo;
- [ ] seção onde foi usado, se aplicável;
- [ ] subseções revisadas no refactoring editorial;
- [ ] motivo se foi descartado/suplantado;
- [ ] comando de validação executado;
- [ ] data da última revisão.

## Definition of done por artefato

Um artefato só é considerado concluído quando:

- [ ] foi gerado por script versionado;
- [ ] possui CSV de dados e metadata;
- [ ] possui figura nos formatos necessários, se for visual;
- [ ] foi validado por teste ou checagem reprodutível;
- [ ] foi inspecionado visualmente, quando figura;
- [ ] foi registrado no `ARTIFACT_USAGE_CATALOG.md`;
- [ ] tem status editorial definido;
- [ ] tem utilidade e limitação descritas;
- [ ] passou por revisão sistêmica das subseções afetadas;
- [ ] tem decisão explícita sobre uso: texto principal, apêndice, resposta,
  diagnóstico, descartado ou suplantado.

## Fontes de dados principais

| Fonte | Caminho | Uso principal |
|---|---|---|
| Student responses | `data/lake/student_responses.parquet` | M1/M2, percepções e uso autorrelatado por checkpoint |
| Evaluator scores | `data/lake/evaluator_team_cuts.parquet` | scores T1/T2/T3, dimensões avaliativas e trajetórias |
| Git commits | `data/lake/git_commits.parquet` | atividade temporal, autoria, regularidade, concentração final |
| Git files | `data/lake/git_files.parquet` | churn limpo, complexidade estrutural, arquivos/diretórios |
| Git team cuts | `data/lake/git_team_cuts.parquet` | checkpoint summaries e lacunas por T1/T2/T3 |
| M3 | `paper_v9/data/metrics/m3_*` | atividade/autoria já agregada |
| M4 | `paper_v9/data/metrics/m4_*` | clean churn já agregado |
| M5 | `paper_v9/data/metrics/m5_*` | marcadores textuais, somente 2025.2 |
| M6a | `paper_v9/data/metrics/m6a_structural_planning.csv` | planejamento estrutural visível no repositório |
| M6b | `paper_v9/data/metrics/m6b_llm_planning_content.json` | evidência textual exploratória de planejamento |
| M7 | `paper_v9/data/metrics/m7_*` | inatividade e padrões temporais |
| M8 | `paper_v9/data/metrics/m8_*` | rework por clean-path provenance |
| M9 | `paper_v9/data/metrics/m9_*` | associações e leave-one-out existentes |

## Priorização geral

| Prioridade | Fase | Benefício | Complexidade | Justificativa |
|---:|---|---|---|---|
| 1 | Score trajectories x concentração final | Muito alto | Baixa-média | Conecta desempenho, planejamento e student syndrome diretamente |
| 2 | Quadrantes planejamento x concentração x score | Muito alto | Baixa | Visual sintético e retoricamente forte |
| 3 | Regularidade operacional via Git | Alto | Média | Mitiga ameaça sobre processos heterogêneos |
| 4 | Influência/sensibilidade expandida | Alto | Média | Mitiga amostra pequena e dominância de casos |
| 5 | Complexidade técnica como confundidor | Alto | Média-alta | Ataca ameaça explícita de heterogeneidade técnica |
| 6 | Bins não sobrepostos e fases | Médio-alto | Média | Mitiga rolling-window overlap |
| 7 | Triangulação M5 restrita a 2025.2 | Médio | Média | Fortalece M5 apesar da cobertura parcial |
| 8 | Painel de evidência team-semester | Médio | Média | Organiza grãos analíticos e dá transparência |
| 9 | Catálogo versionado de uso dos artefatos | Alto | Baixa | Evita reanalisar todos os artefatos a cada decisão editorial |
| 10 | Integração editorial/LaTeX | Alto | Média | Converte análise em melhoria do artigo |

---

# Fase 0 — Preparação e contratos analíticos

## Objetivo

Criar uma base comum para todas as fases seguintes: helpers, definições de
score composto, trajetória avaliativa, planejamento alto/baixo e concentração
final. Esta fase reduz duplicação e evita divergência entre scripts.

## Tarefa 0.1 — Definir score composto por checkpoint

**Input esperado**

- `data/lake/evaluator_team_cuts.parquet`
- Colunas:
  - `project_progress_mean`
  - `scope_applicability_mean`
  - `technical_complexity_mean`
  - `engagement_participation_mean`
  - `ID_Equipe`
  - `Semestre`
  - `temporal_marker`

**Processamento**

- Calcular `evaluator_score_composite` como média das quatro dimensões.
- Produzir uma tabela wide por equipe-semestre:
  - `evaluator_score_t1`
  - `evaluator_score_t2`
  - `evaluator_score_t3`
  - `delta_score_t3_minus_t1`
  - `delta_score_t2_minus_t1`
  - `delta_score_t3_minus_t2`

**Output esperado**

- `paper_v9/figures/rq2_score_trajectory_base_data.csv`
- `paper_v9/figures/rq2_score_trajectory_base.metadata.json`

**Checklist**

- [x] Validar 14 equipe-semestres.
- [x] Validar presença de T1/T2/T3 para evaluator scores.
- [x] Registrar colunas usadas no score composto.
- [x] Registrar que o score composto é descritivo e não uma métrica oficial de qualidade global.

## Tarefa 0.2 — Definir grupos de trajetória avaliativa

**Input esperado**

- `rq2_score_trajectory_base_data.csv`

**Processamento**

Criar categorias:

- `improved`: `delta_score_t3_minus_t1 > +threshold`
- `declined`: `delta_score_t3_minus_t1 < -threshold`
- `stable_high`: variação pequena e score T3 acima da mediana
- `stable_low`: variação pequena e score T3 abaixo da mediana

Threshold inicial recomendado:

- `0.25` ponto no score composto, ou
- threshold baseado em IQR/tercil se a distribuição for estreita.

**Output esperado**

- Coluna `score_trajectory_group`
- Tabela de contagem por grupo.
- `paper_v9/figures/rq2_score_trajectory_group_counts.csv`

**Checklist**

- [x] Verificar se os grupos não ficam excessivamente pequenos.
- [x] Se algum grupo tiver `n < 2`, registrar fallback para 3 grupos:
  - `improved`
  - `stable`
  - `declined`
- [x] Registrar thresholds em metadata.

## Tarefa 0.3 — Definir planejamento alto/baixo

**Input esperado**

- `paper_v9/data/metrics/m6a_structural_planning.csv`

**Processamento**

Criar variáveis:

- `planning_present_t1`
- `planning_scope_log1p_t1`
- `planning_scope_tier`
  - `high_repository_visible_planning`: planejamento presente e escopo >= mediana
  - `lower_repository_visible_planning`: demais casos

**Output esperado**

- Colunas incorporadas ao dataset base.

**Checklist**

- [x] Nomear explicitamente como `repository_visible_planning`.
- [x] Não usar linguagem de “qualidade de planejamento”.
- [x] Registrar mediana usada.

## Tarefa 0.4 — Reaproveitar concentração final já gerada

**Input esperado**

- `paper_v9/figures/rq2_student_syndrome_final7_concentration_by_tier_data.csv`

**Processamento**

- Normalizar nomes de colunas para uso comum:
  - `final7_commit_share_pct`
  - `final7_clean_churn_share_pct`

**Output esperado**

- Merge no dataset base por `ID_Equipe`, `Semestre`.

**Checklist**

- [x] Validar que commits cobrem 14 equipe-semestres.
- [x] Validar cobertura de clean churn.
- [x] Registrar casos com zero clean churn, se aplicável.

---

# Fase 1 — Trajetórias avaliativas x concentração final

## Benefício

Muito alto. Esta fase responde a uma pergunta central para novos achados:

> A concentração tardia de atividade acompanha melhora avaliativa, piora ou
> estabilidade?

Ela fortalece a narrativa ao conectar atividade temporal de repositório com
resultado avaliativo, sem afirmar causalidade.

## Nota de reconciliação da implementação da Fase 1

As tarefas 1.1, 1.2 e 1.4 foram implementadas em um mesmo incremento técnico,
porque o script `paper_v9/scripts/results/generate_score_trajectory_concentration.py`
materializa simultaneamente:

- os dados derivados e figuras exigidos pela Tarefa 1.1;
- os dois scatters previstos pela Tarefa 1.2;
- as validações automatizadas previstas pela Tarefa 1.4 por meio de
  `paper_v9/tests/test_score_trajectory_concentration.py`.

A Tarefa 1.3 foi implementada em incremento posterior com a materialização de
`paper_v9/figures/rq2_score_delta_final7_quadrants.csv`.

Essa consolidação foi feita por coesão técnica dos outputs, mas deve ser tratada
como exceção operacional. Nas próximas fases, a ordem granular das tarefas deve
ser preservada de forma explícita, ou a consolidação de tarefas deve ser
registrada antes do avanço para a fase seguinte.

## Tarefa 1.1 — Script de geração

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_score_trajectory_concentration.py
```

**Input esperado**

- Dataset base da Fase 0.
- `rq2_student_syndrome_final7_concentration_by_tier_data.csv`
- `m6a_structural_planning.csv`
- `evaluator_team_cuts.parquet`

**Output esperado**

- [x] `paper_v9/figures/rq2_score_delta_vs_final7_commit_concentration_data.csv`
- [x] `paper_v9/figures/rq2_score_delta_vs_final7_clean_churn_concentration_data.csv`
- [x] `paper_v9/figures/rq2_score_delta_vs_final7_concentration.metadata.json`
- Figuras:
  - [x] `rq2_score_delta_vs_final7_commit_concentration.{png,svg,pdf}`
  - [x] `rq2_score_delta_vs_final7_clean_churn_concentration.{png,svg,pdf}`

## Tarefa 1.2 — Scatter: concentração final x delta score

**Visualização**

- x-axis: final-seven-day share.
- y-axis: `delta_score_t3_minus_t1`.
- color: `planning_scope_tier`.
- shape: `Semestre`.
- labels/hover: `ID_Equipe`, score T1, score T3.

**Insight esperado**

- Identificar se equipes com alta concentração final melhoram, pioram ou ficam estáveis.
- Separar “recuperação tardia” de “corrida final sem ganho avaliativo”.

**Checklist**

- [x] Criar versão commits.
- [x] Criar versão clean changed lines.
- [x] Incluir linha horizontal em `delta = 0`.
- [x] Incluir linha vertical na mediana de concentração final.
- [x] Exibir pontos individuais.
- [x] Registrar `n` por quadrante.

## Tarefa 1.3 — Tabela de quadrantes

**Input esperado**

- Dados da Tarefa 1.2.

**Output esperado**

- [x] `paper_v9/figures/rq2_score_delta_final7_quadrants.csv`

**Quadrantes**

| Concentração final | Delta score | Interpretação |
|---|---|---|
| Alta | Positivo | Recuperação tardia potencial |
| Alta | Negativo/estável | Student syndrome pouco produtivo |
| Baixa | Positivo | Progresso distribuído |
| Baixa | Negativo/estável | Baixa atividade final sem ganho |

**Checklist**

- [x] Usar mediana como corte de concentração.
- [x] Usar threshold da Fase 0 como corte de delta.
- [x] Reportar contagens por planejamento alto/baixo.

## Tarefa 1.4 — Teste focado

**Arquivo a criar**

```text
paper_v9/tests/test_score_trajectory_concentration.py
```

**Checklist**

- [x] Testar geração dos CSVs.
- [x] Testar geração de PNG/SVG/PDF.
- [x] Testar `n=14` para commits.
- [x] Testar que `delta_score_t3_minus_t1` existe e é numérico.
- [x] Testar que `final7_share_pct` está entre 0 e 100.

---

# Fase 2 — Planejamento x concentração final x resultado

## Benefício

Muito alto e baixo custo. Esta fase produz uma visualização sintética para a
narrativa central: planejamento inicial, padrão temporal de trabalho e resultado.

**Status operacional atual:** implementada e validada após a Fase 1, mas ainda
não commitada. O avanço para fases posteriores deve aguardar confirmação/commit
explícito para preservar a sequência de controle do plano.

## Tarefa 2.1 — Script de geração

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_planning_concentration_quadrants.py
```

**Input esperado**

- Dataset base da Fase 0.
- Concentração final de commits e clean churn.
- M6a planning scope.
- Evaluator score T3 e delta score.

**Output esperado**

- [x] `rq2_planning_vs_final7_commit_concentration_data.csv`
- [x] `rq2_planning_vs_final7_clean_churn_concentration_data.csv`
- [x] `rq2_planning_concentration_quadrants.metadata.json`
- Figuras:
  - [x] `rq2_planning_vs_final7_commit_concentration.{png,svg,pdf}`
  - [x] `rq2_planning_vs_final7_clean_churn_concentration.{png,svg,pdf}`

## Tarefa 2.2 — Quadrant plot

**Visualização**

- x-axis: `planning_scope_log1p_t1`.
- y-axis: final-seven-day concentration.
- color: `evaluator_score_t3`.
- shape: `Semestre`.
- marker size: `delta_score_t3_minus_t1` absoluto ou clean rework.

**Linhas de referência**

- Mediana de planejamento.
- Mediana de concentração final.

**Insight esperado**

Identificar perfis:

- alto planejamento + baixa concentração final + alto T3 score;
- baixo planejamento + alta concentração final + baixo T3 score;
- alto planejamento + alta concentração final;
- baixo planejamento + baixa concentração final.

**Checklist**

- [x] Criar versão commits.
- [x] Criar versão clean changed lines.
- [x] Incluir labels/hover por equipe.
- [x] Registrar contagem por quadrante.
- [x] Evitar chamar o eixo de planejamento de “qualidade”; usar “repository-visible T1 planning scope”.

## Tarefa 2.3 — Sumário narrativo por quadrante

**Output esperado**

- [x] `rq2_planning_concentration_quadrant_summary.csv`

**Colunas**

- `activity_metric`
- `quadrant`
- `team_semester_n`
- `mean_t3_score`
- `median_t3_score`
- `mean_delta_score`
- `median_delta_score`
- `mean_clean_rework_churn_t3`, se disponível

**Checklist**

- [x] Incluir denominadores.
- [x] Registrar se algum quadrante tem `n=0` ou `n=1`.
- [x] Não inferir significância estatística.

---

# Fase 3 — Regularidade operacional como proxy de processo observável

## Benefício

Alto. Esta fase mitiga a ameaça de que processos heterogêneos
Scrum/Kanban/unguided não foram medidos diretamente. Não medimos aderência a
processos, mas podemos medir regularidade operacional observável no Git.

## Tarefa 3.1 — Script de geração de regularidade

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_operational_regularity.py
```

**Input esperado**

- `data/lake/git_commits.parquet`
- `data/lake/git_files.parquet`
- `paper_v9/data/metrics/m3_author_activity_participation.csv`
- `paper_v9/data/metrics/m7_inactivity_trajectory.csv`
- Dataset base da Fase 0.

**Output esperado**

- [x] `rq2_operational_regularity_data.csv`
- [x] `rq2_operational_regularity.metadata.json`

## Tarefa 3.2 — Métricas de regularidade

Calcular por equipe-semestre:

- `active_day_count`
- `project_span_days`
- `active_day_share`
- `max_inactivity_gap_days`
- `median_inactivity_gap_days`
- `commit_weekly_cv`
- `clean_churn_weekly_cv`
- `temporal_entropy_commits`
- `temporal_entropy_clean_churn`
- `final7_commit_share_pct`
- `final7_clean_churn_share_pct`
- `author_count`
- `max_author_share`
- `author_gini`

**Output esperado**

- CSV com uma linha por equipe-semestre.

**Checklist**

- [x] Validar `n=14`.
- [x] Registrar fórmulas no metadata.
- [x] Tratar semanas sem atividade como zeros apenas quando o período de observação estiver definido.
- [x] Separar regularidade de produtividade.

## Tarefa 3.3 — Visualizações de regularidade

Figuras sugeridas:

1. [x] `rq2_regularity_vs_score_delta.{png,svg,pdf}`
   - x: regularity index.
   - y: delta score T3-T1.
   - color: planning tier.

2. [x] `rq2_regularity_vs_final_concentration.{png,svg,pdf}`
   - x: regularity index.
   - y: final-seven-day concentration.
   - color: score trajectory group.

3. [x] `rq2_regularity_profile_heatmap.{png,svg,pdf}`
   - rows: equipe-semestre.
   - columns: regularity metrics z-scored.
   - annotation: planning tier and score trajectory group.

**Definição autorizada do índice**

- [x] `regularity_index` aprovado no Gate B como média de oito componentes normalizados em que maior indica atividade observável mais distribuída:
  - `active_day_share`;
  - `temporal_entropy_commits`;
  - `temporal_entropy_clean_churn`;
  - inverso min-max de `commit_weekly_cv`;
  - inverso min-max de `clean_churn_weekly_cv`;
  - inverso de `m7_inactive_window_share`;
  - inverso de `final7_commit_share_pct / 100`;
  - inverso de `final7_clean_churn_share_pct / 100`.

**Output produzido**

- [x] `rq2_regularity_vs_score_delta_data.csv`
- [x] `rq2_regularity_vs_final_concentration_data.csv`
- [x] `rq2_regularity_profile_heatmap_data.csv`

**Insight esperado**

> Equipes com planejamento visível também apresentam cadência operacional mais
> regular, menor concentração final ou menor inatividade?

## Tarefa 3.4 — Teste focado

**Arquivo a criar**

```text
paper_v9/tests/test_operational_regularity.py
```

**Checklist**

- [x] Testar `n=14`.
- [x] Testar métricas dentro de faixas válidas.
- [x] Testar geração das figuras.
- [x] Testar metadata com fórmulas e limitações.

---

# Fase 4 — Sensibilidade e influência de casos

## Benefício

Alto. Mitiga a ameaça de amostra pequena e dependência de equipe-semestre
influente.

## Tarefa 4.1 — Script de influence map

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_influence_maps.py
```

**Input esperado**

- `paper_v9/data/metrics/m9_leave_one_out_intervals.csv`
- Dataset base da Fase 0.
- Dados das Fases 1, 2 e 3.

**Output esperado**

- [x] `rq3_influence_map_data.csv`
- [x] `rq3_influence_map.metadata.json`
- [x] `rq3_influence_map.{png,svg,pdf}`

**Status de implementação**

- [x] Script reprodutível criado.
- [x] Relações candidatas materializadas no metadata para revisão sistemática na Tarefa 4.2.
- [x] Figura inicial gerada como mapa de influência leave-one-out.
- [x] Relações revisadas/operacionalizadas na Tarefa 4.2.

## Tarefa 4.2 — Relações a avaliar

Calcular leave-one-out para:

- planejamento T1 → T3 score;
- planejamento T1 → delta score T3-T1;
- planejamento T1 → final7 concentration;
- final7 concentration → T3 score;
- final7 concentration → delta score;
- regularity index → delta score;
- technical complexity T3 → clean churn/rework;
- planning T1 → rework T3.

**Métrica**

- Spearman rho descritivo.
- Sinal completo.
- Sinal leave-one-out.
- Variação absoluta em rho ao remover cada equipe.

**Output produzido**

- [x] `rq3_influence_relationship_contract.csv`

**Operacionalização**

- [x] As 8 categorias da Tarefa 4.2 foram mapeadas para 13 relações operacionais:
  - concentração final separada em commits e clean churn;
  - rework separado em magnitude de churn e ratio baseline-eligible.
- [x] Cada relação registra `full_sample_rho`, `full_sample_sign`, `loo_min_rho`, `loo_max_rho`, `max_abs_rho_delta_from_full` e `sign_preservation_share`.

**Checklist**

- [x] Não reportar como teste confirmatório.
- [x] Usar linguagem de “directional robustness”.
- [x] Registrar relações com `n < 4` como indisponíveis.

## Tarefa 4.3 — Heatmap

**Visualização**

- [x] rows: equipe-semestre removida.
- [x] columns: relação avaliada.
- [x] color: mudança no coeficiente (`rho leave-one-out - rho completo`).

**Output produzido**

- [x] `rq3_influence_map.{png,svg,pdf}`
- [x] `rq3_influence_heatmap_matrix.csv`

**Codificação**

- [x] Hover registra rho completo, rho leave-one-out, variação absoluta, sinal completo, sinal leave-one-out e status de disponibilidade.
- [x] Metadata registra `heatmap_encoding`.

**Insight esperado**

> Quais achados são estáveis e quais dependem de uma equipe específica?

## Tarefa 4.4 — Tabela de robustez de sinal

**Output esperado**

- [x] `rq3_directional_robustness_summary.csv`

**Colunas**

- [x] `relationship`
- [x] `full_sample_rho`
- [x] `loo_min_rho`
- [x] `loo_max_rho`
- [x] `sign_preservation_share`
- [x] `most_influential_team_semester`

**Checklist**

- [x] Ordenar por menor preservação de sinal.
- [x] Destacar relações instáveis como achados de sensibilidade, não falhas.

---

# Fase 5 — Complexidade técnica como confundidor

## Benefício

Alto. Ataca uma ameaça explícita: projetos com integrações GenAI
heterogêneas podem ter complexidade técnica diferente.

## Tarefa 5.1 — Script de complexidade

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_complexity_confounding_profiles.py
```

**Input esperado**

- `data/lake/evaluator_team_cuts.parquet`
- `data/lake/git_files.parquet`
- `paper_v9/data/metrics/m4_churn_magnitude.csv`
- `paper_v9/data/metrics/m8_rework_magnitude.csv`
- `paper_v9/data/metrics/m6a_structural_planning.csv`

**Output esperado**

- [x] `rq3_complexity_profile_data.csv`
- [x] `rq3_complexity_profile.metadata.json`

**Status de implementação**

- [x] Script reprodutível criado.
- [x] Perfil base gerado com `n=14` equipe-semestres.
- [x] Metadata registra separação entre complexidade avaliada e complexidade estrutural inferida.
- [x] Metadata registra heurísticas de path usadas para camadas frontend/backend.
- [x] Revisão/validação editorial das métricas concluída na Tarefa 5.2.

## Tarefa 5.2 — Métricas de complexidade

### Complexidade avaliada

- [x] `technical_complexity_mean_t1`
- [x] `technical_complexity_mean_t2`
- [x] `technical_complexity_mean_t3`
- [x] `delta_technical_complexity_t3_minus_t1`

### Complexidade estrutural do repositório

- [x] número de arquivos limpos distintos;
- [x] número de diretórios distintos;
- [x] profundidade máxima de caminho;
- [x] número de extensões;
- [x] proporção backend/frontend, se inferível por path;
- [x] número de commits tocando clean paths;
- [x] diversidade de arquivos por commit;
- [x] churn total limpo.

**Output produzido**

- [x] `rq3_complexity_metrics_contract.csv`

**Operacionalização**

- [x] Métricas avaliadas e estruturais separadas por `construct_family`.
- [x] Cada métrica registra fonte, definição, requisito do plano e heurística/política.
- [x] O contrato registra que não houve classificação manual de arquitetura GenAI.

**Checklist**

- [x] Separar complexidade avaliada de complexidade estrutural inferida.
- [x] Documentar heurísticas de path.
- [x] Não classificar arquitetura GenAI manualmente sem protocolo.

## Tarefa 5.3 — Visualizações

Figuras sugeridas:

1. `rq3_technical_complexity_vs_rework.{png,svg,pdf}`
   - x: technical complexity T3.
   - y: clean rework T3.
   - color: planning tier.

2. `rq3_complexity_vs_final_concentration.{png,svg,pdf}`
   - x: technical complexity T3.
   - y: final-seven-day concentration.
   - color: score trajectory group.

3. `rq3_planning_rework_complexity_overlay.{png,svg,pdf}`
   - x: planning scope T1.
   - y: rework T3.
   - color: technical complexity T3.
   - shape: baseline eligibility.

**Output produzido**

- [x] `rq3_technical_complexity_vs_rework.{png,svg,pdf}`
- [x] `rq3_technical_complexity_vs_rework_data.csv`
- [x] `rq3_complexity_vs_final_concentration.{png,svg,pdf}`
- [x] `rq3_complexity_vs_final_concentration_data.csv`
- [x] `rq3_planning_rework_complexity_overlay.{png,svg,pdf}`
- [x] `rq3_planning_rework_complexity_overlay_data.csv`

**Operacionalização**

- [x] Figura complexidade técnica × rework usa `technical_complexity_mean_t3` no eixo x, `clean_rework_churn_t3` no eixo y e `planning_scope_tier` como cor.
- [x] Figura complexidade × concentração final usa `technical_complexity_mean_t3` no eixo x, concentração final no eixo y e `score_trajectory_group` como cor, com painéis para commits e clean churn.
- [x] Overlay planejamento–rework–complexidade usa `planning_scope_log1p_t1`, `clean_rework_churn_t3`, cor por complexidade técnica T3 e forma por elegibilidade de baseline.
- [x] Metadata registra paths, hashes e contrato visual das três figuras.

**Insight esperado**

> Parte do churn/rework pode refletir complexidade técnica do projeto, não
> somente planejamento fraco ou uso de IA.

## Tarefa 5.4 — Sumário de confounding

**Output esperado**

- [x] `rq3_complexity_confounding_summary.csv`

**Colunas**

- `relationship`
- `rho_without_complexity_stratification`
- `rho_within_low_complexity`
- `rho_within_high_complexity`
- `interpretation_note`

**Checklist**

- [x] Usar estratificação por mediana, não regressão pesada, por causa de `n=14`.
- [x] Registrar quando estratos têm `n` muito baixo.

**Operacionalização**

- [x] Sumário calcula Spearman rho descritivo sem estratificação e dentro de estratos `technical_complexity_mean_t3 <= mediana` e `> mediana`.
- [x] Relações com `clean_rework_ratio_t3` são restritas a casos `baseline_eligible_for_rework_t3=True`.
- [x] Cada linha registra `n` total, `n` por estrato, variável de estratificação, regra de corte e nota interpretativa.
- [x] Associações indisponíveis são registradas quando `n<4` ou quando preditor/desfecho é constante; nenhuma regressão é usada.

---

# Fase 6 — Bins não sobrepostos e fases do projeto

## Benefício

Médio-alto. Mitiga a ameaça de janelas rolling sobrepostas.

## Tarefa 6.1 — Script de bins/fases

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_nonoverlapping_phase_activity.py
```

**Input esperado**

- `data/lake/git_commits.parquet`
- `data/lake/git_files.parquet`
- evaluator form timestamps para anchors T1/T2/T3.
- Dados de planejamento e scores.

**Output esperado**

- [x] `rq2_nonoverlapping_weekly_activity_data.csv`
- [x] `rq2_phase_activity_share_data.csv`
- [x] `rq2_nonoverlapping_phase_activity.metadata.json`
- [x] Figuras exploratórias `rq2_nonoverlapping_weekly_activity_overview.{png,svg,pdf}` e `rq2_phase_activity_share_overview.{png,svg,pdf}`.

**Status de implementação**

- [x] Script reprodutível criado.
- [x] Anchors T1/T2/T3 derivados dos timestamps dos formulários de avaliadores.
- [x] Dados de planejamento/score incorporados a partir de `rq2_score_trajectory_base_data.csv`.
- [x] Artefatos base gerados para `n=14` equipe-semestres.
- [ ] Validação focada de contrato dos bins semanais permanece na Tarefa 6.2.
- [ ] Figuras finais nomeadas por fase permanecem na Tarefa 6.3.

## Tarefa 6.2 — Weekly bins não sobrepostos

Criar bins semanais relativos ao T3:

- `week_-12`
- ...
- `week_-1`
- `final_7_days`

Métricas:

- commits;
- clean changed lines;
- active days;
- autores ativos.

**Checklist**

- [x] Não usar rolling windows.
- [x] Cada evento deve pertencer a exatamente um bin.
- [x] Registrar período coberto e bins vazios.

**Output produzido**

- [x] `rq2_nonoverlapping_weekly_bin_contract.csv`
- [x] `rq2_nonoverlapping_weekly_assignment_audit.csv`

**Operacionalização**

- [x] Contrato semanal registra `week_bin`, ordem, início/fim UTC, dias relativos ao T3, notação `[period_start, period_end)` e `rolling_window_used=False`.
- [x] Auditoria valida, por equipe-semestre e métrica, que eventos cobertos foram atribuídos uma única vez, sem duplicidade e sem eventos não atribuídos.
- [x] Metadata registra contagem de bins vazios para commits, clean churn e bins completamente vazios.

## Tarefa 6.3 — Phase bins

Fases:

- `pre_t1`
- `t1_to_t2`
- `t2_to_t3_excluding_final7`
- `final7_pre_t3`

**Output esperado**

- [x] Share de atividade por fase e equipe-semestre.

**Visualizações**

- [x] `rq2_phase_commit_share_by_score_trajectory.{png,svg,pdf}`
- [x] `rq2_phase_clean_churn_share_by_score_trajectory.{png,svg,pdf}`

**Operacionalização**

- [x] Fases `pre_t1`, `t1_to_t2`, `t2_to_t3_excluding_final7` e `final7_pre_t3` são mutuamente exclusivas por equipe-semestre.
- [x] Shares de commits e clean churn somam 100% por equipe-semestre quando há atividade observada.
- [x] Figuras finais usam `phase_summary` e agrupam por `score_trajectory_group`.
- [x] Metadata registra contrato visual das duas figuras finais.

**Insight esperado**

> O pico final permanece quando agregamos por fases não sobrepostas?

---

# Fase 7 — Triangulação M5 restrita a 2025.2

## Benefício

Médio. Fortalece M5 sem esconder a limitação de cobertura.

## Tarefa 7.1 — Script de triangulação 2025.2

**Arquivo a criar**

```text
paper_v9/scripts/results/generate_m5_2025_triangulation.py
```

**Input esperado**

- `paper_v9/data/metrics/m5_marker_density.csv`
- `paper_v9/data/metrics/m4_churn_magnitude.csv`
- `paper_v9/data/metrics/m8_rework_magnitude.csv`
- `data/lake/evaluator_team_cuts.parquet`
- `m6a_structural_planning.csv`

**Output esperado**

- [x] `rq2_m5_2025_triangulation_data.csv`
- [x] `rq2_m5_2025_triangulation_summary.csv`
- [x] `rq2_m5_2025_triangulation.metadata.json`
- [x] `rq2_m5_2025_triangulation_panel.{png,svg,pdf}`

**Operacionalização**

- [x] Script filtra a triangulação para `2025.2`, único semestre com cobertura M5.
- [x] M5 é repetido por equipe apenas como contexto global por `temporal_marker`, com nota explícita de que não é medida team-level.
- [x] Metadata registra `2026.1` como `unavailable_not_measured` e confirma que semestres indisponíveis não são preenchidos com zero.
- [x] Dados integram M5 marker density, M4 clean churn, M8 T3 rework, score avaliativo composto e M6a planejamento estrutural.

## Tarefa 7.2 — Coverage-aware M5 panel

**Visualização**

- [x] painel restrito a 2025.2;
- [x] M5 marker density por T1/T2/T3;
- [x] M4 clean churn por T1/T2/T3;
- [x] evaluator score por T1/T2/T3;
- [x] M8 T3 clean rework como contexto de rework.

**Insight esperado**

> No semestre com transcritos, marcadores textuais de coordenação/fricção
> acompanham aumento de atividade/rework?

**Checklist**

- [x] Não incluir 2026.1 como zero.
- [x] Marcar explicitamente `2026.1 unavailable_not_measured`.
- [x] Registrar que o corpus é global/transcript-level, não team-semester completo.

---

# Fase 8 — Painel integrado de evidência por equipe-semestre

## Benefício

Médio, mas muito útil para transparência e revisão editorial.

## Tarefa 8.1 — Script de evidence panel

**Arquivo a criar**

```text
paper_v9/scripts/results/build_team_semester_evidence_panel.py
```

**Input esperado**

- Outputs das Fases 0-7.
- M1/M2 summaries, quando agregáveis apenas por semestre/checkpoint.
- M3-M9.

**Output esperado**

- [x] `paper_v9/figures/team_semester_evidence_panel.csv`
- [x] `paper_v9/figures/team_semester_evidence_panel.metadata.json`

## Tarefa 8.2 — Conteúdo do painel

Cada linha: equipe-semestre.

Colunas sugeridas:

- planejamento:
  - `planning_artifact_present_t1`
  - `planning_scope_log1p_t1`
  - `planning_scope_tier`
- avaliação:
  - scores T1/T2/T3
  - delta scores
  - score trajectory group
- atividade:
  - total commits
  - active days
  - final7 commit share
  - final7 clean churn share
  - regularity index
- rework:
  - clean rework T3
  - clean rework ratio T3
  - baseline eligibility
- complexidade:
  - technical complexity T3
  - structural complexity proxies
- cobertura:
  - M5 available?
  - M6b available?
  - missingness flags

**Checklist**

- [x] Não misturar métricas de grão estudante com equipe sem explicitar agregação.
- [x] Incluir colunas de status/cobertura.
- [x] Usar como base para tabelas e apêndices.

---

# Fase 9 — Catálogo versionado de uso dos artefatos

## Benefício

Alto, com baixo custo. Esta fase cria um controle editorial persistente para
evitar reanalisar todos os artefatos sempre que surgir uma pergunta narrativa,
uma revisão de seção ou uma crítica de avaliador. O catálogo deve registrar a
utilidade prática de cada figura/dado, seu status de uso no artigo e a resposta
empírica curta para cada insight esperado já executado.

## Tarefa 9.1 — Criar catálogo inicial de uso

**Arquivo a criar**

```text
paper_v9/ARTIFACT_USAGE_CATALOG.md
```

**Input esperado**

- Artefatos já existentes em `paper_v9/figures/`.
- Metadados `.metadata.json`.
- `FIGURES_CANDIDATES_WORKSHOP.md`.
- `STUDENT_SYNDROME_REVIEW_RESPONSE.md`.
- Outputs das novas fases implementadas.

**Output esperado**

- Um catálogo Markdown versionado com seções por família analítica.

**Estrutura mínima sugerida**

```markdown
# Artifact Usage Catalog

## Status taxonomy

## High-priority main-text candidates

## Artifact families

### student_syndrome

| artifact_id | files | question | best_use | key_reading | utility | limitations | status |
|---|---|---|---|---|---|---|---|

### score_trajectory

...

## Superseded or diagnostic-only artifacts
```

**Checklist**

- [x] Registrar todos os artefatos já gerados sobre student syndrome.
- [x] Registrar artefatos de candidate figures existentes.
- [x] Registrar nova família de score trajectories após Fase 1.
- [x] Registrar nova família de quadrants após Fase 2.
- [x] Usar links relativos para os arquivos.
- [x] Registrar status inicial como `candidate` ou `diagnostic_only`.
- [x] Registrar `last_reviewed`.

## Tarefa 9.2 — Definir taxonomia de status editorial

**Status recomendados**

| Status | Uso |
|---|---|
| `candidate` | Artefato potencialmente útil, ainda não escolhido |
| `main_text` | Artefato selecionado para o corpo principal |
| `appendix` | Artefato útil, mas melhor como material suplementar |
| `response_letter` | Artefato usado principalmente para responder crítica/revisor |
| `diagnostic_only` | Artefato útil para inspeção interna/metodológica |
| `superseded` | Artefato substituído por versão melhor |
| `discarded` | Artefato descartado, com justificativa |

**Checklist**

- [x] Incluir a taxonomia no topo do catálogo.
- [x] Exigir justificativa curta para `superseded` e `discarded`.
- [x] Exigir campo `superseded_by` quando aplicável.

## Tarefa 9.3 — Registrar utilidade e interpretação curta

Para cada artefato, registrar:

- pergunta respondida;
- melhor uso retórico;
- leitura principal;
- limitação principal;
- denominador/grão analítico;
- risco de má interpretação;
- recomendação de uso.

**Exemplo**

```markdown
| artifact_id | rq2_student_syndrome_final7_concentration_by_tier |
| question | A concentração nos 7 dias finais difere por planejamento/desempenho? |
| best_use | Results ou resposta a reviewer |
| key_reading | Lower/weaker-planning teams concentram parcela maior da atividade pré-T3 na semana final. |
| limitation | Não contém telemetria de IA; mede concentração temporal, não causa. |
| status | main_text candidate |
```

**Checklist**

- [x] Manter descrições curtas o suficiente para consulta rápida.
- [x] Evitar reinterpretar causalmente artefatos exploratórios.
- [x] Incluir “quando usar” e “quando não usar”.

## Tarefa 9.4 — Sincronizar catálogo com scripts/metadados

**Input esperado**

- `*.metadata.json` de cada família analítica.

**Output esperado**

- O catálogo deve referenciar os mesmos paths listados nos metadados.

**Checklist**

- [x] Conferir se todos os arquivos listados existem.
- [x] Conferir se o stem do artefato no catálogo corresponde ao metadata.
- [x] Conferir se inputs principais estão coerentes com os metadados.
- [x] Atualizar `last_reviewed` quando houver revisão editorial.

## Tarefa 9.5 — Usar o catálogo como gate editorial

Antes de editar `results.tex`, `discussion.tex` ou `threats_to_validity.tex`:

- [x] Consultar o catálogo completo, não apenas a lista de artefatos.
- [x] Revisar o `Registro de respostas aos insights esperados` para identificar
  quais achados já têm resposta empírica curta, quais ressalvas devem ser
  preservadas e quais insights ainda não devem ser promovidos ao texto.
- [x] Selecionar artefatos com status `candidate`, `main_text` ou `appendix`.
- [x] Evitar reabrir todos os CSVs/figuras sem necessidade.
- [x] Registrar no gate que o status dos artefatos escolhidos deve ser
  atualizado durante a seleção editorial da Fase 10.
- [x] Registrar no gate que artefatos substituídos devem ser documentados antes
  da integração LaTeX.

---

# Fase 10 — Integração no artigo LaTeX

## Benefício

Alto. Sem integração textual, as novas análises não fortalecem o artigo.

## Tarefa 10.1 — Seleção de figuras para texto principal

Critério:

- priorizar mitigação explícita das ameaças à validade discutidas pelo artigo e
  pelos revisores, sem usar economia de páginas como restrição nesta etapa;
- integrar em largura total (`figure*`, `width=\textwidth`) figuras complexas
  ou com muitos detalhes, para preservar legibilidade no PDF;
- mover apenas diagnósticos densos ou artefatos de auditoria para
  suplemento/apêndice;
- priorizar figuras que conectem diretamente planejamento, atividade, resultado,
  complexidade técnica e limitações de cobertura.

Figuras selecionadas para texto principal ou integração principal:

1. `rq2_score_delta_vs_final7_commit_concentration`
2. `rq2_score_delta_vs_final7_clean_churn_concentration`
3. `rq2_planning_vs_final7_commit_concentration`
4. `rq2_planning_vs_final7_clean_churn_concentration`
5. `rq2_phase_commit_share_by_score_trajectory`
6. `rq2_phase_clean_churn_share_by_score_trajectory`
7. `rq2_m5_2025_triangulation_panel`
8. Uma figura de regularidade operacional visualmente clara, preferencialmente
   `rq2_regularity_vs_final_concentration` para Threats ou
   `rq2_regularity_vs_score_delta` para Results.
9. `rq3_technical_complexity_vs_rework` e/ou
   `rq3_planning_rework_complexity_overlay`
10. `rq3_influence_map`

Figuras/tabelas propostas para apêndice, suplemento ou substituição:

- `team_semester_evidence_panel`: apêndice/suplemento, não tabela compacta no
  corpo principal.
- `rq2_regularity_profile_heatmap`: apêndice, por densidade visual.
- `fig:rq2-m3`: manter como evidência de pico bruto ou mover para apêndice
  somente se a integração com fases não sobrepostas preservar a leitura temporal.
- `fig:rq2-m4-m5`: candidato a substituição pelo painel M5 coverage-aware, se o
  texto preferir destacar cobertura e ausência de zero-fill.
- `fig:rq3-sensitivity`: candidato a substituição por `rq3_influence_map`, que
  cobre mais relações e casos influentes.

**Checklist**

- [x] Consultar `ARTIFACT_USAGE_CATALOG.md` como um todo, incluindo status de
  artefatos, limitações e respostas aos insights esperados, antes de selecionar
  figuras.
- [x] Escolher figuras principais priorizando Threats to Validity; a restrição
  original de no máximo 2 novas figuras foi substituída por legibilidade e
  mitigação substantiva das ameaças.
- [x] Escolher figuras/tabelas suplementares.
- [x] Atualizar lista de figuras candidatas se necessário.
- [x] Atualizar status no catálogo para `main_text`, `appendix` ou `diagnostic_only`.

## Tarefa 10.2 — Atualizar Results

**Input esperado**

- Novos summaries e figuras.

**Output esperado**

- Alterações em:
  - `paper_v9/latex/sections/results.tex`

**Parágrafos a incluir**

- Trajetórias avaliativas e concentração final.
- Planejamento visível e distribuição temporal.
- Regularidade operacional, se fase concluída.
- Complexidade técnica como explicação concorrente, se fase concluída.

**Checklist**

- [x] Reportar denominadores.
- [x] Reportar `n` por estrato.
- [x] Evitar linguagem causal.
- [x] Não repetir toda a seção de Threats.
- [x] Referenciar artefatos cuja utilidade esteja registrada no catálogo.
- [x] Usar as respostas registradas para os insights esperados como guia de
  síntese, preservando números principais e ressalvas.

Validação: PDF recompilado com `TEXINPUTS=.:../:` a partir de
`paper_v9/latex`; as figuras densas foram renderizadas em largura total. O log
final de `latex/main.pdf` não registra erros de imagem, labels indefinidos,
citações indefinidas ou floats pendentes.

## Tarefa 10.3 — Atualizar Discussion

**Input esperado**

- Interpretações dos novos achados.

**Output esperado**

- Alterações em:
  - `paper_v9/latex/sections/discussion.tex`

**Foco**

- Distinguir:
  - procrastinação produtiva/compensatória;
  - concentração tardia sem ganho avaliativo;
  - execução distribuída;
  - complexidade técnica.

**Checklist**

- [x] Conectar achados à narrativa de coordenação/especificação.
- [x] Manter SDD como hipótese/intervenção futura.
- [x] Não afirmar que os dados testam SDD.
- [x] Usar as interpretações curtas e as respostas aos insights esperados do
  catálogo como ponto de partida, não como substituto da análise textual.

Validação: Discussion atualizada com distinção entre execução tardia
compensatória/produtiva, concentração tardia sem ganho avaliativo, execução
distribuída e complexidade técnica como explicação concorrente; SDD permanece
como intervenção futura plausível, não como tratamento testado.

## Tarefa 10.4 — Atualizar Threats to Validity

**Input esperado**

- Mitigações geradas.

**Output esperado**

- Alterações em:
  - `paper_v9/latex/sections/threats_to_validity.tex`

**Orientação**

Transformar algumas ameaças de:

> "cannot be disentangled"

para:

> "we mitigate this by reporting internal contrasts / non-overlapping bins /
> influence maps, but causal and external validity remain limited."

**Checklist**

- [x] Não remover limitações estruturais.
- [x] Atualizar student syndrome com as análises realizadas.
- [x] Atualizar rolling windows se bins não sobrepostos forem implementados.
- [x] Atualizar small sample se influence maps forem implementados.
- [x] Atualizar process heterogeneity se regularity proxies forem implementados.
- [x] Atualizar complexity confounding se fase 5 for implementada.

Validação: Threats to Validity atualizada para preservar limites causais e
externos, mas registrar mitigações por contrastes internos de student syndrome,
bins/fases não sobrepostas, mapas de influência leave-one-out, proxies de
regularidade operacional, perfis de complexidade técnica e cobertura explícita
de M5.

## Tarefa 10.5 — Compilar LaTeX

**Comando esperado**

Usar o comando já estabelecido no projeto para compilar o paper.

**Checklist**

- [x] Compilar sem erros.
- [x] Verificar referências de figuras.
- [x] Verificar captions.
- [x] Verificar se figuras em PDF/SVG/PNG estão disponíveis no caminho esperado.

Validação: `paper_v9/latex/main.pdf` e `paper_v9/latex/build/main.pdf`
gerados com 27 páginas após sequência `pdflatex`/`bibtex`/`pdflatex`. Os logs
finais não registram citações indefinidas, referências indefinidas, erros de
imagem, overfull hboxes ou floats pendentes. Verificação automática encontrou
18 chamadas `includegraphics`, 25 captions e nenhum arquivo de figura ausente.

---

# Fase 11 — Atualização de documentação e reproducibilidade

## Tarefa 11.1 — Atualizar inventário de figuras

**Arquivo**

```text
paper_v9/FIGURES_CANDIDATES_WORKSHOP.md
```

**Checklist**

- [x] Adicionar novas famílias de figuras.
- [x] Indicar força e limitação de cada uma.
- [x] Marcar quais são candidatas ao texto principal.
- [x] Sincronizar com `ARTIFACT_USAGE_CATALOG.md`.

Validação: `FIGURES_CANDIDATES_WORKSHOP.md` atualizado como inventário
editorial sincronizado com `ARTIFACT_USAGE_CATALOG.md`. Foram verificados 18
stems de figuras em formatos `{pdf,svg,png}`, sem arquivos ausentes, além do
CSV suplementar `team_semester_evidence_panel.csv`.

## Tarefa 11.2 — Atualizar reproducibilidade

**Arquivo**

```text
paper_v9/REPRODUCIBILITY.md
```

**Checklist**

- [x] Adicionar comandos dos novos scripts.
- [x] Adicionar testes focados.
- [x] Indicar inputs e outputs.
- [x] Indicar que decisões editoriais sobre artefatos são rastreadas em `ARTIFACT_USAGE_CATALOG.md`.

Validação: `REPRODUCIBILITY.md` recebeu uma seção dedicada ao pipeline de
artefatos de robustez, com comandos executáveis a partir da raiz do
repositório, entradas/saídas por família analítica, testes focados existentes
e nota de governança que mantém `ARTIFACT_USAGE_CATALOG.md` como plano de
controle editorial.

## Tarefa 11.3 — Atualizar results summary

**Possível arquivo/script**

- `paper_v9/scripts/results/build_results_summary.py`
- `paper_v9/data/results/results_summary.json`

**Checklist**

- [x] Decidir se os novos artefatos entram no catálogo oficial.
- [x] Se sim, incluir em `METRIC_FILES` ou em nova seção de robustness artifacts.
- [x] Regenerar summary.
- [x] Testar `paper_v9/tests/test_results_summary.py`.

Decisão: manter `METRIC_FILES` restrito às métricas oficiais M1--M9 e adicionar
uma seção separada `robustness_artifacts`, governada por
`ARTIFACT_USAGE_CATALOG.md`, para registrar figuras, dados e metadados de
robustez/editoriais sem tratá-los como novas métricas causais.

Validação:

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m py_compile paper_v9/scripts/results/build_results_summary.py paper_v9/tests/test_results_summary.py
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python paper_v9/scripts/results/build_results_summary.py
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m pytest paper_v9/tests/test_results_summary.py
```

---

# Ordem recomendada de implementação

## Sprint 1 — Alto retorno, baixa/média complexidade

- [ ] Fase 0 — contratos base.
- [ ] Fase 1 — score trajectory x final concentration.
- [ ] Fase 2 — planning x final concentration x score.
- [ ] Fase 9 — criar/atualizar catálogo de uso dos artefatos para as novas figuras.
- [ ] Testes focados das Fases 1 e 2.
- [ ] Revisão visual das figuras.

**Resultado esperado**

Um conjunto mínimo e forte de novos achados:

> Como concentração tardia, planejamento inicial e evolução avaliativa se
> relacionam?

## Sprint 2 — Mitigação metodológica forte

- [ ] Fase 3 — regularidade operacional.
- [ ] Fase 4 — influence maps.
- [ ] Fase 6 — bins não sobrepostos/fases.
- [ ] Fase 9 — atualizar status, utilidade e limitações dos artefatos gerados.

**Resultado esperado**

Mitigar ameaças sobre:

- processos heterogêneos;
- amostra pequena;
- janelas sobrepostas.

## Sprint 3 — Confundidores e triangulação

- [ ] Fase 5 — complexidade técnica.
- [ ] Fase 7 — triangulação M5 2025.2.
- [ ] Fase 8 — evidence panel.
- [ ] Fase 9 — registrar artefatos candidatos, diagnósticos e substituídos.

**Resultado esperado**

Tratar ameaças sobre:

- complexidade técnica;
- fricção textual;
- grãos analíticos.

## Sprint 4 — Integração no artigo

- [ ] Fase 9 — revisar catálogo como gate editorial.
- [ ] Fase 10 — integração Results/Discussion/Threats.
- [ ] Fase 11 — documentação/reprodutibilidade.
- [ ] Compilação LaTeX.
- [ ] Revisão final de coerência.

---

# Critérios de decisão: quando parar ou mover para apêndice

Uma análise deve ir para o texto principal se:

- [ ] conecta diretamente planejamento, atividade e resultado;
- [ ] tem denominadores claros;
- [ ] não depende de um único outlier;
- [ ] possui figura legível;
- [ ] contribui para a narrativa central do artigo.
- [ ] está registrada no catálogo com `utility_score` alto ou justificativa explícita.

Uma análise deve ir para apêndice/suplemento se:

- [ ] é diagnóstica, mas visualmente densa;
- [ ] reforça uma ameaça metodológica sem gerar achado substantivo;
- [ ] tem muitos estratos com `n <= 2`;
- [ ] serve principalmente para transparência.
- [ ] está registrada no catálogo como `appendix` ou `diagnostic_only`.

Uma análise deve ser descartada ou apenas documentada se:

- [ ] exige imputação indevida;
- [ ] mistura grãos analíticos sem denominador claro;
- [ ] sugere causalidade que os dados não suportam;
- [ ] replica informação já mostrada por figura mais simples.
- [ ] tem justificativa registrada no catálogo como `discarded` ou `superseded`.

---

# Mapeamento Threats to Validity -> fases do plano

| Ameaça em `Threats to Validity` | Fase que mitiga | Status esperado |
|---|---|---|
| Self-report não é telemetria objetiva de IA | Fase 8 e integração textual | Mitigação interpretativa, não resolução |
| M6a/M6b não provam qualidade/intent | Fases 2, 3, 8 | Triangulação parcial |
| M8 não é defeito semântico | Fases 5, 8 | Triangulação com score/churn/complexidade |
| M5 não diagnostica fricção diretamente | Fase 7 | Triangulação restrita a 2025.2 |
| Student syndrome | Fases 1, 2, 6 | Mitigação forte |
| Sem grupo controle não-IA | Todas, por contrastes internos | Não resolvido |
| Amostra pequena/influência de casos | Fase 4 | Mitigação forte |
| Grãos analíticos diferentes | Fase 8 | Mitigação forte de transparência |
| Rolling windows sobrepostos | Fase 6 | Mitigação forte |
| Transcript coverage só 2025.2 | Fase 7 | Mitigação parcial |
| Processos heterogêneos não medidos | Fase 3 | Mitigação parcial via proxy Git |
| Git não observa planejamento off-repo | Fases 2, 3, 8 | Mitigação parcial |
| Missing M6b T1 subjects | Fase 8 | Mitigação por perfil de missingness |
| Complexidade técnica heterogênea | Fase 5 | Mitigação forte |
| SDD não testado | Integração textual | Não resolvido; manter como hipótese futura |

Observação operacional: quando uma fase gerar artefatos para mitigar uma
ameaça, a relação ameaça -> artefato deve ser registrada em
`ARTIFACT_USAGE_CATALOG.md`. Isso permite localizar rapidamente quais figuras
ou tabelas sustentam cada revisão futura da seção `Threats to Validity`.

---

# Comandos de validação esperados

Após cada fase implementada:

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m py_compile <novo_script.py> <novo_teste.py>
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m pytest <novo_teste.py>
```

Após cada sprint:

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m pytest paper_v9/tests
```

Antes de integrar ao artigo:

```bash
git --no-pager status --short
```

---

# Entregáveis finais esperados

## Scripts

- [x] `generate_score_trajectory_concentration.py`
- [x] `generate_planning_concentration_quadrants.py`
- [x] `generate_operational_regularity.py`
- [x] `generate_influence_maps.py`
- [x] `generate_complexity_confounding_profiles.py`
- [x] `generate_nonoverlapping_phase_activity.py`
- [x] `generate_m5_2025_triangulation.py`
- [x] `build_team_semester_evidence_panel.py`

## Testes

- [x] `test_score_trajectory_concentration.py`
- [x] `test_planning_concentration_quadrants.py`
- [x] `test_operational_regularity.py`
- [x] `test_influence_maps.py`
- [x] `test_complexity_confounding_profiles.py`
- [x] `test_nonoverlapping_phase_activity.py`
- [x] `test_m5_2025_triangulation.py`
- [x] `test_team_semester_evidence_panel.py`

## Figuras principais candidatas

- [x] Score delta vs final concentration.
- [x] Planning scope vs final concentration colored by T3 score.
- [x] Regularity vs score delta.
- [x] Influence heatmap.
- [x] Complexity vs rework/concentration.

## Controle versionado de uso dos artefatos

- [x] `ARTIFACT_USAGE_CATALOG.md`
- [x] Status editorial de cada artefato.
- [x] Breve descrição da utilidade de cada artefato.
- [x] Limitação principal de cada artefato.
- [x] Relação com seção do artigo ou ameaça de validade.
- [x] Registro de artefatos substituídos/descartados.

## Integração editorial

- [x] Atualizar `results.tex`.
- [x] Atualizar `discussion.tex`.
- [x] Atualizar `threats_to_validity.tex`.
- [x] Atualizar documentação de figuras.
- [x] Atualizar reprodutibilidade.
- [x] Compilar LaTeX.

Validação final de sprint:

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python -m pytest paper_v9/tests
```

Resultado final em 2026-09-25: `58 passed, 2 warnings`.

---

# Definição de sucesso

O plano será considerado implementado com sucesso quando:

- [x] As novas análises produzirem artefatos reprodutíveis com metadados.
- [x] Cada família analítica tiver teste focado.
- [x] Cada família analítica estiver registrada no catálogo versionado de uso
  com utilidade, limitação, status e melhor contexto editorial.
- [x] As figuras selecionadas para o texto principal tiverem interpretação
  clara e denominadores explícitos.
- [x] Nenhuma figura for promovida ao texto principal sem status atualizado no
  catálogo.
- [x] A seção `Threats to Validity` for atualizada para refletir as mitigações
  sem remover limitações estruturais.
- [x] A narrativa do artigo distinguir melhor:
  - atividade tardia;
  - planejamento visível;
  - regularidade operacional;
  - evolução avaliativa;
  - complexidade técnica;
  - limitações causais.
