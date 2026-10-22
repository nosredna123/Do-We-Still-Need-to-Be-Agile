Vou ler a seção de ameaças e cruzá-la com os artefatos v9 existentes para separar o que pode ser mitigado com novas agregações do que é limitação estrutural dos dados.

Read , lines 1 to 120
Completed with input: {
  "path": "/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/paper_v9/latex/sections/threats_to_validity.tex",
  "view_range": [
    1,
    120
  ]
}

Read , lines 1 to 90
Completed with input: {
  "path": "/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/paper_v9/INPUTS_SUMMARY.md",
  "view_range": [
    1,
    90
  ]
}

Read , lines 1 to 220
Completed with input: {
  "path": "/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/paper_v9/data/results/results_summary.json",
  "view_range": [
    1,
    220
  ]
}

Sim — dá para fortalecer bastante o trabalho explorando melhor os dados já existentes. Mas eu separaria os pontos da seção **Threats to Validity** em três categorias:

1. **Limitações estruturais que não conseguimos resolver com os dados atuais**;
2. **Limitações que podemos mitigar com novas agregações/estratificações**;
3. **Limitações que podem virar achados adicionais se cruzarmos melhor planejamento, atividade e avaliação**.

Abaixo faço esse mapeamento com base na seção `threats_to_validity.tex`.

---

## 1. Limitações que os dados atuais não resolvem totalmente

### 1.1 Falta de telemetria objetiva de uso de IA

Trecho da ameaça:

> M1 and M2 rely exclusively on self-reported survey measures rather than objective behavioral telemetry.

Isso **não é resolvível** com os dados atuais. Não temos:

- logs de Copilot;
- chamadas de API;
- acceptance rate de sugestões;
- timestamps reais de uso de ferramentas de IA;
- associação direta entre uso de IA e commit.

O que podemos fazer é **mitigar interpretativamente**, não resolver. Por exemplo:

- cruzar percepções de uso de IA por checkpoint com atividade de repositório por checkpoint;
- verificar se períodos com maior percepção de uso coincidem com maior churn, rework ou fricção textual;
- mostrar que os achados não dependem de tratar M1/M2 como telemetria.

Mas a frase precisa continuar sendo:

> “AI usage is self-reported and cannot be interpreted as objective behavioral telemetry.”

Uma nova análise pode fortalecer a narrativa, mas não eliminar essa ameaça.

---

### 1.2 Ausência de grupo controle não-IA

Trecho:

> Without a non-AI control group, we cannot determine whether these delays reflect GenAI-related architectural debt or conventional late-stage integration pressure.

Também **não é resolvível** com os dados atuais. Todos os projetos tinham componente GenAI. Então não conseguimos comparar:

- equipes com IA versus equipes sem IA;
- arquitetura tradicional versus arquitetura GenAI;
- turma GenAI versus turma controle.

O que podemos fazer é **substituir a comparação ausente por contrastes internos**:

- maior versus menor planejamento;
- maior versus menor escore avaliativo;
- maior versus menor concentração tardia;
- maior versus menor rework;
- maior versus menor complexidade técnica avaliada.

Isso não cria causalidade, mas permite dizer:

> “Within the GenAI-only sample, late concentration varies with planning and evaluation profiles.”

Ou seja, não resolve o problema do controle, mas melhora a granularidade interna.

---

### 1.3 Validade externa: 14 team-semesters em um contexto educacional

Trecho:

> The study covers 14 team-semesters in one educational setting.

Isso também **não é resolvível** com os dados atuais. Não há como transformar 14 casos educacionais em evidência generalizável para indústria.

Mas podemos mitigar de duas formas:

1. **Mostrar heterogeneidade interna**:
   - dois semestres;
   - equipes diferentes;
   - projetos diferentes;
   - integrações GenAI diferentes;
   - níveis variados de planejamento, atividade e resultado.

2. **Evitar depender de uma média agregada única**:
   - usar gráficos por equipe;
   - leave-one-out;
   - bootstrap;
   - distribuições por team-semester;
   - análise por semestre.

Isso reduz a ameaça de “o resultado é só um caso dominante”, mas não amplia o universo externo.

---

## 2. Limitações que podemos mitigar bem com novas análises

Aqui estão os pontos mais promissores.

---

## 2.1 “Student syndrome” e concentração tardia

Trecho:

> The late-stage concentration of Repository Activity (M3) and Clean-Change Dynamics (M4) cannot be disentangled from ordinary student procrastination.

Esse ponto já começou a ser mitigado com os novos artefatos.

Arquivos relevantes:

- `rq2_student_syndrome_final7_concentration_by_tier.png`
- `rq2_student_syndrome_full_period_commits_by_tier.png`
- `rq2_student_syndrome_full_period_clean_churn_by_tier.png`
- `STUDENT_SYNDROME_REVIEW_RESPONSE.md`

Mas ainda podemos ir além.

### Novas variações possíveis

#### A. Concentração final × mudança de score

- x-axis: final-seven-day activity share;
- y-axis: `T3 score - T1 score`;
- color: planejamento alto/baixo;
- shape: semestre;
- duas versões:
  - commits;
  - clean changed lines.

Insight possível:

> Equipes que concentram atividade no final melhoram de fato, ou apenas trabalham tardiamente sem ganho avaliativo proporcional?

Isso mitigaria a ameaça de interpretar late activity como produtividade.

#### B. Concentração final × score T3

- x-axis: concentração final;
- y-axis: score avaliativo final;
- color: planejamento T1;
- facet: commits vs clean churn.

Insight possível:

> Maior concentração final está associada a melhor resultado final ou a resultado mais fraco?

Isso ajuda a separar:

- “trabalho final produtivo”;
- “corrida final improdutiva”;
- “deadline effect geral”.

#### C. Trajetórias de score

Classificar equipes como:

- improved;
- stable high;
- stable low;
- declined.

Depois comparar a atividade temporal desses grupos.

Insight possível:

> Equipes que melhoram têm atividade mais distribuída, ou também concentram no final?

Esse seria um achado muito alinhado com a narrativa atual do artigo.

---

## 2.2 Sensibilidade a poucos casos / amostra pequena

Trecho:

> M9 associations are exploratory ... leave-one-out ranges show sensitivity to individual team-semesters.

Isso pode ser **fortemente mitigado**, embora não resolvido.

Já existe alguma base:

- `m9_leave_one_out_intervals.csv`
- `rq3_association_sensitivity.png`

Mas podemos expandir.

### Novas variações possíveis

#### A. Influence map por equipe

Para cada equipe-semestre, mostrar quanto sua remoção altera:

- associação planejamento → rework;
- associação planejamento → evaluator score;
- associação concentração final → score;
- associação clean churn → score.

Visual:

- heatmap;
- rows = team-semesters;
- columns = relações avaliadas;
- color = mudança no coeficiente ao remover o caso.

Insight possível:

> Quais equipes são influentes? Os achados dependem de uma única equipe?

Isso melhora muito a credibilidade.

#### B. Small-multiple scatterplots com labels

Para M9 e novas relações score/activity:

- todos os pontos visíveis;
- cada equipe identificável;
- não esconder outliers em média agregada.

Insight possível:

> O artigo se torna mais transparente sobre a escala pequena da amostra.

#### C. Robust direction-of-effect table

Em vez de focar p-value, reportar:

- sinal da associação;
- mediana leave-one-out;
- intervalo leave-one-out;
- número de remoções que preservam o sinal.

Exemplo:

| Relação | Sinal completo | % leave-one-out preservando sinal |
|---|---:|---:|
| planejamento T1 → rework T3 | negativo | 86% |
| concentração final → score T3 | negativo | 71% |

Isso é excelente para estudo exploratório.

---

## 2.3 Grãos analíticos incompatíveis

Trecho:

> Analytical grains differ across student responses, team-semesters, rolling windows, and a global transcript corpus, so denominators cannot be pooled implicitly.

Essa ameaça é **parcialmente mitigável** criando painéis que deixam o grão explícito.

### Problema atual

Temos métricas em níveis diferentes:

- M1/M2: estudante/checkpoint;
- M3/M4/M7: equipe-semestre/janela temporal;
- M5: corpus textual/transcritos, só 2025.2;
- M6/M8/M9: equipe-semestre;
- M9: associações agregadas.

### Nova possibilidade

Criar um **Team-Semester Evidence Panel**.

Cada linha = uma equipe-semestre.

Colunas possíveis:

- planejamento T1:
  - `planning_artifact_present_t1`;
  - `planning_scope_log1p_t1`;
- atividade:
  - total commits;
  - final-seven-day commit share;
  - final-seven-day clean churn share;
  - inactivity pattern;
- rework:
  - clean rework churn T3;
  - clean rework ratio T3;
- avaliação:
  - score T1;
  - score T2;
  - score T3;
  - Δscore T3-T1;
- texto/transcritos:
  - somente se 2025.2;
  - marker density T1/T2/T3 se aplicável;
  - estado “unavailable_not_measured” para 2026.1.

Insight possível:

> O artigo poderia mostrar que as integrações principais são feitas no nível team-semester e que métricas em outros grãos entram apenas como evidência complementar.

Isso não muda os dados, mas reduz a ambiguidade metodológica.

---

## 2.4 Rolling windows sobrepostos

Trecho:

> Rolling windows overlap, so adjacent values are not independent observations.

Essa ameaça pode ser **bem mitigada** com versões não sobrepostas ou por fase.

### Novas agregações possíveis

#### A. Non-overlapping weekly bins

Em vez de janelas diárias sobrepostas de 7 dias:

- semana -8;
- semana -7;
- ...
- semana -1;
- semana final.

Métricas:

- commits por semana;
- clean changed lines por semana;
- active days por semana;
- authors por semana.

Insight possível:

> O pico final permanece quando usamos semanas não sobrepostas?

Se sim, reduzimos a dependência de janelas rolling.

#### B. Phase bins

Separar por fases:

- antes de T1;
- T1→T2;
- T2→T3;
- últimos 7 dias;
- pós-T3, se relevante.

Insight possível:

> A concentração final é robusta a uma agregação por fases do curso, não apenas a janelas rolling.

Isso seria ótimo para responder à própria ameaça metodológica.

#### C. Area under curve por fase

Calcular a proporção de atividade em cada fase.

Exemplo:

| Equipe | T1→T2 share | T2→T3 share | final 7d share |
|---|---:|---:|---:|

Isso pode substituir parte dos gráficos densos por uma métrica mais interpretável.

---

## 2.5 Transcript coverage só em 2025.2

Trecho:

> transcript evidence is available only for 2025.2, which restricts cross-cohort comparability for the lexical findings.

Isso não pode ser resolvido para 2026.1, mas pode ser melhor mitigado.

### Variações possíveis

#### A. Análise M5 estritamente 2025.2

Em vez de apresentar M5 como parte geral da amostra, tratá-lo como:

> “textual corroboration for the 2025.2 cohort only.”

Visual:

- M5 density T1/T2/T3 para 2025.2;
- lado a lado com M3/M4 das mesmas equipes 2025.2;
- sem tentar comparar com 2026.1.

Insight possível:

> Para o semestre em que há transcritos, aumento de marcadores de coordenação acompanha aumento de atividade/rework?

#### B. Coverage-aware evidence matrix

Mostrar explicitamente:

| Métrica | 2025.2 | 2026.1 |
|---|---:|---:|
| Git commits | disponível | disponível |
| Git files | disponível | disponível |
| Evaluator scores | disponível | disponível |
| Surveys | disponível | disponível |
| Transcripts | disponível | indisponível |

Isso não é um achado novo, mas aumenta transparência.

#### C. Within-2025.2 triangulation

Cruzar:

- M5 marker density;
- M3/M4 activity;
- M8 rework;
- evaluator score;
- planejamento M6a.

Insight possível:

> Em 2025.2, as equipes com maior evidência textual de coordenação/fricção também apresentam mais churn/rework ou pior trajetória avaliativa?

Isso transforma uma limitação em uma análise de triangulação restrita.

---

## 2.6 Processos heterogêneos: Scrum, Kanban, unguided etc.

Trecho:

> teams had complete autonomy over their process models ... the study neither standardized these processes nor measured adherence to them.

Não podemos medir aderência real a Scrum/Kanban sem dados externos. Mas podemos derivar **proxies comportamentais de processo** a partir do Git.

### Possíveis proxies

#### A. Regularidade de commits

- número de dias ativos;
- maior gap sem commits;
- coeficiente de variação de commits semanais;
- entropia temporal de commits;
- concentração final.

Insight:

> Equipes com atividade mais regular tiveram melhor trajetória avaliativa?

#### B. Distribuição de autoria

- número de autores;
- Gini de commits por autor;
- max author share;
- mudança de autoria ao longo do tempo.

Já há base em M3.

Insight:

> Equipes com atividade concentrada em poucos autores apresentam mais concentração tardia ou pior resultado?

#### C. Continuidade versus bursts

- número de bursts;
- duração média de bursts;
- atividade contínua T1→T3;
- gaps antes de T3.

Insight:

> O problema é simplesmente “menos planejamento” ou também “processo mais episódico”?

Isso mitigaria a ameaça de processo heterogêneo ao mostrar que, mesmo sem saber se usaram Scrum/Kanban, conseguimos medir regularidade operacional observável.

---

## 2.7 Git não observa planejamento/colaboração fora do repositório

Trecho:

> Git cannot observe planning or collaboration outside the repositories.

Essa ameaça não é resolvível, mas pode ser mitigada por triangulação.

### Possíveis mitigações

#### A. Separar explicitamente “repository-visible planning”

Em todos os plots e tabelas, usar nomes como:

- repository-visible planning;
- T1 planning artifact evidence;
- planning artifact scope;
- not overall planning quality.

Isso evita overclaim.

#### B. Cruzar M6a com M6b

M6a:

- artefatos estruturais de planejamento no repo.

M6b:

- evidência textual de planejamento em commit subjects.

Se ambos apontam na mesma direção, fortalece a validade construtiva.

Insight:

> Equipes com planejamento estrutural também usam linguagem de planejamento em commits?

Cuidado: M6b tem missingness.

#### C. Cruzar planejamento visível com regularidade posterior

Mesmo que planejamento off-repo não seja observado, podemos perguntar:

> Equipes com planejamento visível no repo apresentam atividade posterior mais regular?

Isso não prova planejamento real, mas valida se o proxy tem algum comportamento esperado.

---

## 2.8 M6b com casos sem T1 commit subjects

Trecho:

> Five Planning Content Evidence (M6b) cases lacked T1 commit subjects and were not measured.

Não é resolvível sem novos dados. Mas dá para mitigar.

### Variações possíveis

#### A. Missingness profile

Comparar casos com M6b disponível versus indisponível em:

- commits T1;
- planning artifact present;
- evaluator T1/T3;
- final concentration;
- clean churn.

Insight:

> A ausência de M6b é aleatória ou está concentrada em equipes com pouca atividade inicial?

Isso é muito importante. Se M6b está ausente justamente onde há pouca atividade T1, isso vira achado metodológico.

#### B. Use M6a como fallback, mas sem imputar M6b

Podemos dizer:

> “M6b missingness is not imputed, but M6a provides repository-visible structural planning coverage for all 14 team-semesters.”

Isso reduz a perda analítica.

---

## 2.9 Complexidade arquitetural como confundidor

Trecho:

> heterogeneous, self-selected AI integrations differed in technical complexity, so architectural complexity remains a potential project-level confound.

Esse ponto é **bem promissor** para mitigar com dados atuais.

Temos pelo menos três caminhos:

### A. Usar score de technical complexity dos avaliadores

Em `evaluator_team_cuts.parquet`, há:

- `technical_complexity_mean`;
- por equipe;
- por T1/T2/T3.

Podemos cruzar:

- technical complexity T3;
- clean churn;
- rework;
- planning;
- final concentration.

Insight:

> Projetos mais complexos tiveram mais churn/rework independentemente de planejamento?

### B. Criar proxy estrutural de complexidade do repositório

A partir de Git/files:

- número de arquivos limpos;
- número de extensões;
- número de diretórios;
- presença de backend/frontend;
- número de componentes;
- churn total;
- diversidade de arquivos alterados;
- binary events;
- touched modules.

Insight:

> O efeito atribuído a planejamento pode na verdade refletir complexidade estrutural?

### C. Classificar integração GenAI

Com dados de repositório e talvez M6b/README/source:

- chatbot simples;
- API wrapper;
- multi-agent;
- document processing;
- RAG-like partial;
- workflow automation.

A seção diz que nenhum implementou RAG completo, mas ainda há heterogeneidade de integração.

Insight:

> Certos tipos de integração GenAI geram mais churn/rework ou atividade tardia?

Esse seria um achado novo muito interessante.

---

## 2.10 Métricas proxy não são qualidade/produtividade

Trecho:

> prevent the metrics from being treated as interchangeable measures of quality, effort, or productivity.

Essa ameaça pode ser mitigada por **triangulação explícita**, não por uma métrica única.

### Estratégia

Criar uma matriz de convergência:

| Fenômeno | Proxy 1 | Proxy 2 | Proxy 3 | Resultado |
|---|---|---|---|---|
| atividade tardia | commits | clean churn | active days | convergente? |
| planejamento | M6a | M6b | regularidade pós-T1 | convergente? |
| fricção | M5 markers | M8 rework | churn burstiness | convergente? |
| resultado | evaluator score | score delta | technical complexity | convergente? |

Insight:

> Quando múltiplos proxies apontam na mesma direção, a interpretação é mais robusta; quando divergem, isso vira achado.

Esse tipo de painel fortaleceria muito a narrativa metodológica.

---

# Oportunidades mais fortes para novos achados

Se o objetivo é fortalecer o artigo, eu priorizaria estas cinco frentes.

---

## Prioridade 1 — Trajetórias de score × atividade temporal

Pergunta:

> Como a evolução avaliativa das equipes se relaciona com a distribuição temporal do trabalho?

Dados:

- evaluator scores T1/T2/T3;
- commits;
- clean changed lines;
- planning M6a.

Visualizações:

1. score trajectory groups;
2. full-period activity por trajetória;
3. final concentration versus Δscore.

Achado potencial:

> Equipes que melhoram apresentam atividade mais distribuída ou conseguem recuperar no final?

---

## Prioridade 2 — Planejamento × concentração final × resultado

Pergunta:

> Planejamento inicial diferencia concentração tardia produtiva de concentração tardia improdutiva?

Dados:

- M6a planning scope;
- final-seven-day share;
- evaluator T3 score;
- Δscore T3-T1.

Visualizações:

1. quadrant plot;
2. scatter planning vs final concentration, colorido por T3 score;
3. bubble plot com clean churn.

Achado potencial:

> Baixo planejamento + alta concentração final pode caracterizar uma forma mais clara de student syndrome com menor retorno avaliativo.

---

## Prioridade 3 — Complexidade técnica como confundidor

Pergunta:

> As associações entre planejamento, churn e resultado mudam quando consideramos complexidade técnica?

Dados:

- technical_complexity_mean T1/T2/T3;
- structural repo complexity;
- clean churn;
- rework;
- planning.

Visualizações:

1. technical complexity vs clean churn;
2. technical complexity vs rework;
3. planning vs rework colorido por technical complexity.

Achado potencial:

> Parte do churn/rework pode refletir complexidade do projeto, não apenas falha de planejamento.

Isso dialoga diretamente com a seção de ameaças.

---

## Prioridade 4 — Regularidade operacional como proxy de processo

Pergunta:

> Sem medir Scrum/Kanban diretamente, conseguimos observar padrões operacionais que sugerem processo mais contínuo ou episódico?

Dados:

- Git commits;
- active days;
- inactivity windows M7;
- author concentration M3;
- final concentration.

Visualizações:

1. regularity index por equipe;
2. regularity vs score;
3. regularity vs planning;
4. regularity vs rework.

Achado potencial:

> Equipes com planejamento visível também tendem a apresentar cadência mais regular e menor concentração final.

Isso mitigaria a ameaça sobre processo heterogêneo.

---

## Prioridade 5 — Triangulação 2025.2 com transcritos

Pergunta:

> No semestre com transcript coverage, fricção textual acompanha fricção observável no repositório?

Dados:

- M5 marker density;
- M4 clean churn;
- M8 rework;
- evaluator score;
- planning.

Visualizações:

1. M5 vs clean churn por checkpoint;
2. M5 vs rework;
3. M5 trajectory alongside activity trajectory.

Achado potencial:

> Marcadores linguísticos de coordenação/fricção aumentam junto com churn/rework perto do T3.

Isso fortalece M5 apesar da limitação de cobertura.

---

# Mapeamento resumido: ameaça → mitigação possível

| Ameaça atual | Mitigável com dados atuais? | Melhor nova análise |
|---|---:|---|
| Self-report não é telemetria objetiva de IA | Parcialmente | Triangulação M1/M2 com Git/evaluator, mas sem causalidade |
| M6a/M6b não provam qualidade/intent | Parcialmente | Convergência M6a × M6b × regularidade posterior |
| M8 não é defeito semântico | Parcialmente | Triangular M8 com churn, score e complexity |
| M5 não diagnostica fricção diretamente | Parcialmente | Triangulação 2025.2 M5 × M4/M8/evaluator |
| Student syndrome | Sim, bem | Já iniciado; adicionar Δscore × final concentration |
| Sem grupo controle não-IA | Não | Apenas contrastes internos |
| Amostra pequena/influência de casos | Sim, bem | Influence maps, leave-one-out expanded |
| Grãos analíticos diferentes | Sim | Team-semester evidence panel |
| Rolling windows sobrepostos | Sim | Weekly non-overlapping bins e phase bins |
| Transcript coverage só 2025.2 | Parcialmente | Análise restrita 2025.2 + coverage-aware matrix |
| Processos heterogêneos não medidos | Parcialmente | Regularity/process proxies via Git |
| Git não observa planejamento off-repo | Parcialmente | Nomear como repository-visible + triangulação |
| Missing M6b T1 subjects | Parcialmente | Missingness profile + M6a fallback sem imputação |
| Heterogeneidade de complexidade técnica | Sim, bem | Technical complexity + repo complexity controls |
| SDD não foi testado | Não | Apenas motivação para estudo futuro |

---

# Minha recomendação

Se você quer fortalecer a narrativa com maior retorno analítico, eu faria uma nova leva chamada algo como:

> **“Evaluator-score trajectory and repository-process robustness analyses”**

Com quatro saídas principais:

1. **Score trajectory classification**
   - improved;
   - stable high;
   - stable low;
   - declined.

2. **Final concentration × score delta**
   - commits;
   - clean changed lines;
   - colorido por planejamento.

3. **Planning × final concentration × T3 score quadrant**
   - uma figura muito narrativa.

4. **Operational regularity index**
   - atividade distribuída versus episódica;
   - cruzada com planejamento, score e rework.

Essas análises atacariam diretamente várias ameaças atuais:

- student syndrome;
- processo heterogêneo;
- proxy validity;
- amostra pequena;
- complexidade/confounding;
- interpretação de atividade como produtividade.

A mensagem retórica seria:

> “Embora os dados continuem observacionais e baseados em proxies, exploramos variações internas de trajetória avaliativa, planejamento visível, regularidade operacional e concentração tardia para distinguir padrões compatíveis com procrastinação, execução distribuída e possível recuperação tardia.”

Isso fortaleceria muito o trabalho sem ultrapassar os limites dos dados.