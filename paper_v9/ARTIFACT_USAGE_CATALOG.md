# Catálogo versionado de uso dos artefatos — paper_v9

Este catálogo registra o uso editorial e analítico dos artefatos gerados para
o `paper_v9`. Ele deve ser consultado antes de criar novas figuras, tabelas ou
dados derivados, para evitar duplicação e para preservar a memória de decisões
editoriais.

## Regra operacional para novos insights

Daqui em diante, toda tarefa/fase que tenha um bloco **Insight esperado** deve
atualizar a seção **Registro de respostas aos insights esperados** assim que os
artefatos correspondentes forem gerados e validados. A resposta deve registrar
o insight em forma curta, as tarefas executadas, os artefatos de evidência, uma
resposta empírica breve, o uso editorial sugerido e as ressalvas. Se a tarefa
ainda produzir apenas infraestrutura sem evidência suficiente para responder ao
insight, isso deve ser declarado no catálogo ou no plano como pendência.

## Taxonomia de status editorial

| Status | Uso | Exigência adicional |
|---|---|---|
| `candidate` | Artefato tecnicamente válido, ainda sem decisão editorial final. | Registrar melhor uso provável e limitação principal. |
| `main_text` | Artefato selecionado para o corpo principal. | Registrar seção/subseção de uso antes da integração LaTeX. |
| `appendix` | Artefato adequado para apêndice/suplemento. | Registrar por que não precisa estar no corpo principal. |
| `response_letter` | Artefato usado principalmente para responder revisão. | Registrar crítica ou pergunta de revisor que o artefato endereça. |
| `diagnostic_only` | Artefato útil para decisão interna/metodológica, mas não recomendado como figura/tabela do artigo. | Registrar risco de má interpretação se promovido. |
| `superseded` | Artefato substituído por versão melhor. | Obrigatório preencher `superseded_by` e explicar em `key_reading` ou `limitations` por que foi substituído. |
| `discarded` | Artefato descartado após revisão. | Obrigatório manter `superseded_by` como `—` e explicar em `limitations` a justificativa curta do descarte. |

Para `superseded` e `discarded`, a justificativa deve ser suficiente para que
uma revisão editorial futura não precise reabrir todos os CSVs/figuras apenas
para entender por que o artefato não deve ser promovido.

## Registro de respostas aos insights esperados

Esta seção registra, de forma editorialmente rastreável, a resposta empírica
curta para cada **Insight esperado** cuja tarefa já foi executada. As respostas
devem ser lidas como sínteses descritivas small-n, não como inferências causais.

| Insight | Tarefas | Artefatos de evidência | Resposta empírica curta | Uso editorial sugerido | Ressalvas |
|---|---|---|---|---|---|
| Alta concentração final melhora, piora ou estabiliza o score? Como separar recuperação tardia de corrida final sem ganho? | Fase 1 / Tarefas 1.1–1.4 | [`figures/rq2_score_delta_vs_final7_commit_concentration_data.csv`](figures/rq2_score_delta_vs_final7_commit_concentration_data.csv), [`figures/rq2_score_delta_vs_final7_clean_churn_concentration_data.csv`](figures/rq2_score_delta_vs_final7_clean_churn_concentration_data.csv), [`figures/rq2_score_delta_final7_quadrants.csv`](figures/rq2_score_delta_final7_quadrants.csv), [`figures/rq2_score_delta_vs_final7_concentration.metadata.json`](figures/rq2_score_delta_vs_final7_concentration.metadata.json) | A concentração final não tem uma leitura única: há casos de `higher_final7_concentration__positive_delta` classificados como possível recuperação tardia e casos de `higher_final7_concentration__negative_or_stable_delta` classificados como corrida final sem ganho avaliativo. Em commits, há 5 equipe-semestres com alta concentração final e delta positivo contra 2 com alta concentração final sem ganho; em clean churn, há 5 contra 2 no mesmo contraste. Também existem casos de baixa concentração final com ganho, sugerindo progresso distribuído. | Results/RQ2 para separar visualmente recuperação tardia de concentração final improdutiva; Discussion para evitar tratar pico final como automaticamente negativo. | `delta_score_t3_minus_t1` usa score composto descritivo; bins por mediana e threshold de delta são small-n; concentração final é proxy temporal, não evidência causal de procrastinação. |
| Quais perfis aparecem ao cruzar planejamento T1, concentração final e resultado T3? | Fase 2 / Tarefas 2.1–2.3 | [`figures/rq2_planning_vs_final7_commit_concentration_data.csv`](figures/rq2_planning_vs_final7_commit_concentration_data.csv), [`figures/rq2_planning_vs_final7_clean_churn_concentration_data.csv`](figures/rq2_planning_vs_final7_clean_churn_concentration_data.csv), [`figures/rq2_planning_concentration_quadrant_summary.csv`](figures/rq2_planning_concentration_quadrant_summary.csv), [`figures/rq2_planning_concentration_quadrants.metadata.json`](figures/rq2_planning_concentration_quadrants.metadata.json) | Os quatro perfis previstos existem. O quadrante `high_repository_visible_planning__lower_final7_concentration` tem 4 equipe-semestres e T3 mediano ≈2.44; `lower_repository_visible_planning__higher_final7_concentration` tem 4 equipe-semestres em commits, T3 mediano ≈2.24 e maior rework médio no recorte de commits. Há também alta concentração com alto planejamento e baixa concentração com baixo planejamento, indicando que escopo de planejamento observável não determina sozinho a distribuição temporal da atividade. | Results/RQ2 como tipologia descritiva dos padrões de planejamento/concentração; Discussion para nuance entre planejamento repositório-visível, concentração final e resultado. | Planejamento mede escopo estrutural observado no repositório, não qualidade semântica; quadrantes dependem de medianas; rework e score não devem ser lidos causalmente. |
| Equipes com planejamento visível têm cadência operacional mais regular, menor concentração final ou menor inatividade? | Fase 3 / Tarefas 3.1–3.4 | [`figures/rq2_operational_regularity_data.csv`](figures/rq2_operational_regularity_data.csv), [`figures/rq2_regularity_vs_score_delta_data.csv`](figures/rq2_regularity_vs_score_delta_data.csv), [`figures/rq2_regularity_vs_final_concentration_data.csv`](figures/rq2_regularity_vs_final_concentration_data.csv), [`figures/rq2_regularity_profile_heatmap_data.csv`](figures/rq2_regularity_profile_heatmap_data.csv), [`figures/rq2_operational_regularity.metadata.json`](figures/rq2_operational_regularity.metadata.json) | Sim, de forma fraca e descritiva: o tier de alto planejamento tem mediana de `regularity_index` ≈0.55 contra ≈0.48 no tier inferior; também tem menor mediana de concentração final de commits (≈28.6% contra ≈48.6%), menor concentração final de clean churn (≈24.2% contra ≈61.8%) e menor share de janelas inativas M7 (≈0.38 contra ≈0.62). | Discussion/Threats como evidência de que regularidade observável no Git ajuda a contextualizar concentração final e planejamento. | O índice de regularidade foi autorizado como composto descritivo, não escala latente validada; Git não mede aderência a Scrum/Kanban, produtividade ou trabalho fora do repositório. |
| Quais achados são estáveis e quais dependem de uma equipe específica? | Fase 4 / Tarefas 4.1–4.4 | [`figures/rq3_influence_map_data.csv`](figures/rq3_influence_map_data.csv), [`figures/rq3_influence_heatmap_matrix.csv`](figures/rq3_influence_heatmap_matrix.csv), [`figures/rq3_influence_relationship_contract.csv`](figures/rq3_influence_relationship_contract.csv), [`figures/rq3_directional_robustness_summary.csv`](figures/rq3_directional_robustness_summary.csv), [`figures/rq3_influence_map.metadata.json`](figures/rq3_influence_map.metadata.json) | A maioria das relações avaliadas preserva o sinal em leave-one-out (`sign_preservation_share=1.0`). As relações mais sensíveis são `technical_complexity_to_rework_ratio` (`sign_preservation_share≈0.71`, caso mais influente `TEAM_07 · 2025.2`) e `planning_scope_to_rework_ratio` (`≈0.86`, caso mais influente `TEAM_08 · 2025.2`). Outras relações relevantes, como planejamento → concentração final, regularidade → delta de score e concentração final → T3 score, preservam direção nas remoções leave-one-out disponíveis. | Threats/Discussion para demonstrar sensibilidade small-n e indicar quais relações são mais dependentes de casos específicos. | Leave-one-out é diagnóstico descritivo, não teste confirmatório; mudanças de sinal indicam dependência de casos, não falha da análise; relações de rework ratio usam baseline eligibility. |
| Parte do churn/rework pode refletir complexidade técnica, não somente planejamento fraco ou uso de IA? | Fase 5 / Tarefas 5.1–5.4 | [`figures/rq3_complexity_profile_data.csv`](figures/rq3_complexity_profile_data.csv), [`figures/rq3_complexity_metrics_contract.csv`](figures/rq3_complexity_metrics_contract.csv), [`figures/rq3_technical_complexity_vs_rework_data.csv`](figures/rq3_technical_complexity_vs_rework_data.csv), [`figures/rq3_complexity_vs_final_concentration_data.csv`](figures/rq3_complexity_vs_final_concentration_data.csv), [`figures/rq3_planning_rework_complexity_overlay_data.csv`](figures/rq3_planning_rework_complexity_overlay_data.csv), [`figures/rq3_complexity_confounding_summary.csv`](figures/rq3_complexity_confounding_summary.csv), [`figures/rq3_complexity_profile.metadata.json`](figures/rq3_complexity_profile.metadata.json) | Sim, como possibilidade contextual/descritiva. O sumário estratificado por mediana de complexidade técnica preserva a direção de planejamento → rework churn em ambos os estratos (rho baixo≈+0.45; alto≈+0.26), mas várias outras relações mudam de direção entre estratos, incluindo planejamento → final-7 concentração e final-7 concentração → rework churn. Isso indica que complexidade técnica pode alterar a leitura de associações entre planejamento, concentração final e rework. | Discussion/Threats como mitigação da interpretação simplista “mais rework = pior planejamento/uso de IA”; base para linguagem de confundimento/sensibilidade. | Estratificação por mediana com n=14, não regressão; complexidade técnica é avaliação humana, enquanto métricas estruturais são heurísticas Git/path; não é ajuste causal. |
| O pico final permanece quando agregamos por fases não sobrepostas? | Fase 6 / Tarefas 6.1–6.3 | [`figures/rq2_nonoverlapping_weekly_activity_data.csv`](figures/rq2_nonoverlapping_weekly_activity_data.csv), [`figures/rq2_nonoverlapping_weekly_bin_contract.csv`](figures/rq2_nonoverlapping_weekly_bin_contract.csv), [`figures/rq2_nonoverlapping_weekly_assignment_audit.csv`](figures/rq2_nonoverlapping_weekly_assignment_audit.csv), [`figures/rq2_phase_activity_share_data.csv`](figures/rq2_phase_activity_share_data.csv), [`figures/rq2_phase_activity_share_summary.csv`](figures/rq2_phase_activity_share_summary.csv), [`figures/rq2_phase_commit_share_by_score_trajectory.png`](figures/rq2_phase_commit_share_by_score_trajectory.png), [`figures/rq2_phase_clean_churn_share_by_score_trajectory.png`](figures/rq2_phase_clean_churn_share_by_score_trajectory.png), [`figures/rq2_nonoverlapping_phase_activity.metadata.json`](figures/rq2_nonoverlapping_phase_activity.metadata.json) | Sim, principalmente para `improved` e `declined`, mas não uniformemente para `stable`. Em fases não sobrepostas, `improved` concentra em média ≈56.7% dos commits e ≈59.0% do clean churn no `final7_pre_t3`; `declined` concentra ≈32.9% dos commits e ≈45.0% do clean churn; `stable` concentra menos no final (≈24.6% commits; ≈18.2% clean churn) e mais em `t1_to_t2`. | Results/RQ2 ou apêndice como robustez contra a crítica de janelas rolling sobrepostas; Discussion para mostrar que o pico final permanece em agregação por fases, mas varia por trajetória de score. | Fases são baseadas em anchors de avaliação e Git observado; `pre_t1` tem duração variável; shares são descritivos e não capturam trabalho fora do repositório. |
| No semestre com transcritos, marcadores textuais de coordenação/fricção acompanham aumento de atividade/rework? | Fase 7 / Tarefas 7.1–7.2 | [`figures/rq2_m5_2025_triangulation_data.csv`](figures/rq2_m5_2025_triangulation_data.csv), [`figures/rq2_m5_2025_triangulation_summary.csv`](figures/rq2_m5_2025_triangulation_summary.csv), [`figures/rq2_m5_2025_triangulation_panel.png`](figures/rq2_m5_2025_triangulation_panel.png), [`figures/rq2_m5_2025_triangulation.metadata.json`](figures/rq2_m5_2025_triangulation.metadata.json) | Em 2025.2, a densidade global de marcadores M5 aumenta de ≈0.52 para ≈1.13 e ≈1.29 por 1k tokens em T1/T2/T3. No mesmo recorte, a mediana de clean churn por equipe sobe de 0 para 2,803 e 5,837, e a mediana do score avaliativo composto sobe de ≈2.00 para ≈2.22 e ≈2.41. O rework limpo é observado em T3 como contexto adicional, com 7/9 equipes baseline-eligible e mediana de 262 linhas de rework. | Results/RQ2 ou Discussion como triangulação coverage-aware limitada ao semestre com transcritos; Threats para explicitar que M5 não cobre 2026.1 e não deve ser zero-filled. | M5 é corpus global por checkpoint, não medida por equipe-semestre; o alinhamento temporal é descritivo e não causal; M8 só mede rework em T3 e não valida defeito semântico; 2026.1 está `unavailable_not_measured`. |

## Artefatos registrados

## Matriz rápida de uso editorial

Esta matriz complementa as entradas detalhadas abaixo. Ela serve como consulta
rápida para decidir quando usar ou evitar cada família sem reler todos os
artefatos.

| Artefato | Quando usar | Quando não usar / risco de má interpretação |
|---|---|---|
| `rq2_score_trajectory_base` | Para recuperar score T1/T2/T3, deltas, grupo de trajetória, planejamento T1 e concentração final em uma base comum. | Não usar como métrica oficial de qualidade global; o score composto é descritivo. |
| `rq2_nonoverlapping_phase_activity` | Para discutir robustez contra janelas rolling sobrepostas e comparar shares por fases mutuamente exclusivas. | Não usar para inferir produtividade fora do Git ou comparar durações absolutas de `pre_t1`. |
| `rq2_m5_2025_triangulation` | Para triangulação coverage-aware entre M5, churn, score e rework no semestre com transcritos. | Não usar como evidência team-level de M5 nem preencher 2026.1 como zero. |
| `team_semester_evidence_panel` | Para apêndice, auditoria editorial e seleção de evidências por equipe-semestre. | Não usar como modelo estatístico ou como prova causal; contém grãos repetidos explicitamente marcados. |
| `rq2_operational_regularity` | Para contextualizar planejamento/concentração com regularidade operacional observável no Git. | Não usar como medida validada de processo ágil, produtividade ou aderência Scrum/Kanban. |
| `rq3_influence_map` | Para Threats/Discussion sobre sensibilidade small-n e dependência de casos específicos. | Não ler intervalos leave-one-out como intervalos de confiança ou significância confirmatória. |
| `rq3_complexity_profile` | Para contextualizar churn/rework e concentração final por complexidade técnica/estrutural. | Não usar como ajuste causal; métricas estruturais são heurísticas Git/path. |
| `rq2_score_delta_vs_final7_concentration` | Para separar recuperação tardia de concentração final sem ganho avaliativo. | Não interpretar concentração final como causa de melhora/piora no score. |
| `rq2_planning_concentration_quadrants` | Para sintetizar perfis planejamento × concentração final × resultado. | Não tratar quadrantes por mediana como classificação substantiva forte. |
| `rq2_student_syndrome_reviewer_response` | Para responder ao revisor e explicitar a alternativa de student syndrome. | Não usar para afirmar que IA causou picos tardios; não há telemetria timestamped de IA. |
| `candidate_figure_inventory` | Para recuperar candidatos exploratórios iniciais durante seleção editorial. | Não promover sem comparar com artefatos mais recentes das Fases 1–8. |

### rq2_score_trajectory_base

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_score_trajectory_base` |
| `artifact_family` | `score_trajectory` |
| `files` | [`figures/rq2_score_trajectory_base_data.csv`](figures/rq2_score_trajectory_base_data.csv), [`figures/rq2_score_trajectory_group_counts.csv`](figures/rq2_score_trajectory_group_counts.csv), [`figures/rq2_score_trajectory_base.metadata.json`](figures/rq2_score_trajectory_base.metadata.json) |
| `data_inputs` | `data/lake/evaluator_team_cuts.parquet`; `paper_v9/data/metrics/m6a_structural_planning.csv`; `paper_v9/figures/rq2_student_syndrome_final7_concentration_by_tier_data.csv` |
| `unit_of_analysis` | equipe-semestre |
| `main_question` | Como o score avaliativo composto varia entre T1, T2 e T3 para cada equipe-semestre, e como essa trajetória se combina com planejamento repositório-visível em T1 e concentração final de atividade? |
| `best_use` | Base comum para Results/Discussion/Threats; input para fases posteriores de trajetórias avaliativas |
| `key_reading` | Artefato contratual: calcula scores compostos T1/T2/T3, deltas, grupos de trajetória, tier de planejamento repositório-visível e concentração final de commits/clean churn por equipe-semestre. Com fallback registrado, os grupos atuais são `improved` (n=8), `stable` (n=4) e `declined` (n=2). O corte de planejamento divide 7 casos em `high_repository_visible_planning` e 7 em `lower_repository_visible_planning`. Commits cobrem 14 equipe-semestres; clean churn cobre 14, com `TEAM_08`/`2025.2` tendo 0% de clean churn nos sete dias finais. |
| `utility_score` | Alta |
| `limitations` | Score composto descritivo, calculado como média não ponderada de quatro dimensões avaliativas; não é métrica oficial de qualidade global nem telemetria objetiva de uso de IA. Os grupos de trajetória são bins descritivos em amostra pequena e usam fallback porque o corte inicial de 0.25 não produziu grupo `declined` suficiente. Planejamento repositório-visível mede presença/escopo estrutural em T1, não qualidade semântica do planejamento. Concentração final é proxy temporal de atividade, não evidência causal. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq2_nonoverlapping_phase_activity

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_nonoverlapping_phase_activity` |
| `artifact_family` | `nonoverlapping_activity_bins` |
| `files` | [`figures/rq2_nonoverlapping_weekly_activity_data.csv`](figures/rq2_nonoverlapping_weekly_activity_data.csv), [`figures/rq2_nonoverlapping_weekly_activity_summary.csv`](figures/rq2_nonoverlapping_weekly_activity_summary.csv), [`figures/rq2_nonoverlapping_weekly_bin_contract.csv`](figures/rq2_nonoverlapping_weekly_bin_contract.csv), [`figures/rq2_nonoverlapping_weekly_assignment_audit.csv`](figures/rq2_nonoverlapping_weekly_assignment_audit.csv), [`figures/rq2_nonoverlapping_weekly_activity_overview.png`](figures/rq2_nonoverlapping_weekly_activity_overview.png), [`figures/rq2_nonoverlapping_weekly_activity_overview.svg`](figures/rq2_nonoverlapping_weekly_activity_overview.svg), [`figures/rq2_nonoverlapping_weekly_activity_overview.pdf`](figures/rq2_nonoverlapping_weekly_activity_overview.pdf), [`figures/rq2_phase_activity_share_data.csv`](figures/rq2_phase_activity_share_data.csv), [`figures/rq2_phase_activity_share_summary.csv`](figures/rq2_phase_activity_share_summary.csv), [`figures/rq2_phase_activity_share_overview.png`](figures/rq2_phase_activity_share_overview.png), [`figures/rq2_phase_activity_share_overview.svg`](figures/rq2_phase_activity_share_overview.svg), [`figures/rq2_phase_activity_share_overview.pdf`](figures/rq2_phase_activity_share_overview.pdf), [`figures/rq2_phase_commit_share_by_score_trajectory.png`](figures/rq2_phase_commit_share_by_score_trajectory.png), [`figures/rq2_phase_commit_share_by_score_trajectory.svg`](figures/rq2_phase_commit_share_by_score_trajectory.svg), [`figures/rq2_phase_commit_share_by_score_trajectory.pdf`](figures/rq2_phase_commit_share_by_score_trajectory.pdf), [`figures/rq2_phase_clean_churn_share_by_score_trajectory.png`](figures/rq2_phase_clean_churn_share_by_score_trajectory.png), [`figures/rq2_phase_clean_churn_share_by_score_trajectory.svg`](figures/rq2_phase_clean_churn_share_by_score_trajectory.svg), [`figures/rq2_phase_clean_churn_share_by_score_trajectory.pdf`](figures/rq2_phase_clean_churn_share_by_score_trajectory.pdf), [`figures/rq2_nonoverlapping_phase_activity.metadata.json`](figures/rq2_nonoverlapping_phase_activity.metadata.json) |
| `data_inputs` | `data/lake/git_commits.parquet`; `data/lake/git_files.parquet`; `data/processed/forms/2025.2/avaliadores.csv`; `data/processed/forms/2026.1/avaliadores.csv`; `paper_v9/figures/rq2_score_trajectory_base_data.csv` |
| `unit_of_analysis` | equipe-semestre × bin semanal; equipe-semestre × fase |
| `main_question` | O padrão de concentração final permanece quando a atividade é reagrupada em bins semanais e fases mutuamente exclusivas, em vez de janelas rolling sobrepostas? |
| `best_use` | Base para Fase 6; Results/Threats como mitigação da ameaça de janelas rolling sobrepostas após validação das Tarefas 6.2 e 6.3 |
| `key_reading` | Artefato base, contratual e visual: cria 13 bins semanais não sobrepostos relativos ao T3 (`week_-12` a `week_-1` e `final_7_days`) e quatro fases não sobrepostas (`pre_t1`, `t1_to_t2`, `t2_to_t3_excluding_final7`, `final7_pre_t3`). As métricas incluem commits distintos, clean changed lines, dias ativos e autores ativos, com zeros preservados para bins vazios. O contrato semanal registra períodos `[start,end)`, ausência de rolling windows e auditoria de atribuição única de eventos. Os shares de fase somam 100% por equipe-semestre para commits e clean churn. As figuras finais da Tarefa 6.3 mostram shares médios por fase e grupo de trajetória de score para testar se o pico final permanece sob agregação não sobreposta. |
| `utility_score` | Alta |
| `limitations` | Atividade Git não observa trabalho fora do repositório; `pre_t1` tem duração variável porque começa no primeiro evento repositório-visível observado antes de T3; os bins semanais cobrem os 91 dias finais antes de T3 e excluem atividade anterior; clean churn depende da política de clean paths vigente. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq2_m5_2025_triangulation

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_m5_2025_triangulation` |
| `artifact_family` | `m5_coverage_aware_triangulation` |
| `files` | [`figures/rq2_m5_2025_triangulation_data.csv`](figures/rq2_m5_2025_triangulation_data.csv), [`figures/rq2_m5_2025_triangulation_summary.csv`](figures/rq2_m5_2025_triangulation_summary.csv), [`figures/rq2_m5_2025_triangulation_panel.png`](figures/rq2_m5_2025_triangulation_panel.png), [`figures/rq2_m5_2025_triangulation_panel.svg`](figures/rq2_m5_2025_triangulation_panel.svg), [`figures/rq2_m5_2025_triangulation_panel.pdf`](figures/rq2_m5_2025_triangulation_panel.pdf), [`figures/rq2_m5_2025_triangulation.metadata.json`](figures/rq2_m5_2025_triangulation.metadata.json) |
| `data_inputs` | `paper_v9/data/metrics/m5_marker_density.csv`; `paper_v9/data/metrics/m5_corpus_coverage.csv`; `paper_v9/data/metrics/m4_churn_magnitude.csv`; `paper_v9/data/metrics/m8_rework_magnitude.csv`; `data/lake/evaluator_team_cuts.parquet`; `paper_v9/data/metrics/m6a_structural_planning.csv` |
| `unit_of_analysis` | equipe × checkpoint para M4/score/planning/rework contextual; M5 global por `temporal_marker` no corpus de transcritos 2025.2 |
| `main_question` | No único semestre com transcritos M5, marcadores textuais globais de coordenação/fricção variam na mesma direção que atividade Git e score avaliativo? |
| `best_use` | Results/RQ2 ou Discussion como triangulação restrita a 2025.2; Threats para documentar cobertura M5 |
| `key_reading` | Artefato coverage-aware: integra M5 marker density global por T1/T2/T3 com M4 clean churn, score avaliativo composto, M8 T3 rework e M6a planejamento para 9 equipes de 2025.2. O painel mostra aumento de M5 density, clean churn mediano e score mediano entre T1 e T3, preservando a ressalva de que M5 não é team-level e que 2026.1 é `unavailable_not_measured`. |
| `utility_score` | Média |
| `limitations` | M5 é global/transcript-level por checkpoint, não equipe-semestre; não há cobertura de 2026.1; rework M8 aparece apenas em T3; associações são descritivas e não causais. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### team_semester_evidence_panel

| Campo | Valor |
|---|---|
| `artifact_id` | `team_semester_evidence_panel` |
| `artifact_family` | `integrated_evidence_panel` |
| `files` | [`figures/team_semester_evidence_panel.csv`](figures/team_semester_evidence_panel.csv), [`figures/team_semester_evidence_panel.metadata.json`](figures/team_semester_evidence_panel.metadata.json) |
| `data_inputs` | `paper_v9/figures/rq2_score_trajectory_base_data.csv`; `paper_v9/figures/rq2_operational_regularity_data.csv`; `paper_v9/figures/rq3_complexity_profile_data.csv`; `paper_v9/figures/rq2_phase_activity_share_data.csv`; `paper_v9/figures/rq2_m5_2025_triangulation_summary.csv`; `paper_v9/data/metrics/m1_rq1_perception_panel_wide.csv`; `paper_v9/data/metrics/m2_role_perception_by_team_semester.csv`; `paper_v9/data/metrics/m6b_llm_planning_content.json` |
| `unit_of_analysis` | equipe-semestre; inclui agregados M1/M2 por semestre/checkpoint repetidos com campo de grão explícito e contexto M5 global restrito a 2025.2 |
| `main_question` | Como reunir, em uma única tabela auditável, as evidências por equipe-semestre usadas nas análises de planejamento, atividade, score, regularidade, rework, complexidade e cobertura? |
| `best_use` | Appendix/suplemento; base de revisão editorial, tabelas de evidência e checagem de cobertura antes da integração textual |
| `key_reading` | Painel integrador com 14 linhas, uma por equipe-semestre. Consolida planejamento M6a, score/deltas, atividade Git, regularidade, rework M8, complexidade, shares por fase, status M6b e cobertura M5. Campos `m1_aggregation_level`, `m2_aggregation_level`, `m5_analysis_level`, `m5_team_level_measure` e `m5_zero_filled_unavailable_semesters` tornam explícito quando uma métrica não é originalmente team-level. |
| `utility_score` | Alta |
| `limitations` | Não é modelo estatístico nem evidência causal; M1/M2 são agregados por semestre/checkpoint; M5 é contexto global de corpus apenas para 2025.2; M6b depende de disponibilidade de commit subjects T1. |
| `status` | `appendix` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq2_operational_regularity

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_operational_regularity` |
| `artifact_family` | `operational_regularity` |
| `files` | [`figures/rq2_operational_regularity_data.csv`](figures/rq2_operational_regularity_data.csv), [`figures/rq2_regularity_vs_score_delta.png`](figures/rq2_regularity_vs_score_delta.png), [`figures/rq2_regularity_vs_score_delta.svg`](figures/rq2_regularity_vs_score_delta.svg), [`figures/rq2_regularity_vs_score_delta.pdf`](figures/rq2_regularity_vs_score_delta.pdf), [`figures/rq2_regularity_vs_score_delta_data.csv`](figures/rq2_regularity_vs_score_delta_data.csv), [`figures/rq2_regularity_vs_final_concentration.png`](figures/rq2_regularity_vs_final_concentration.png), [`figures/rq2_regularity_vs_final_concentration.svg`](figures/rq2_regularity_vs_final_concentration.svg), [`figures/rq2_regularity_vs_final_concentration.pdf`](figures/rq2_regularity_vs_final_concentration.pdf), [`figures/rq2_regularity_vs_final_concentration_data.csv`](figures/rq2_regularity_vs_final_concentration_data.csv), [`figures/rq2_regularity_profile_heatmap.png`](figures/rq2_regularity_profile_heatmap.png), [`figures/rq2_regularity_profile_heatmap.svg`](figures/rq2_regularity_profile_heatmap.svg), [`figures/rq2_regularity_profile_heatmap.pdf`](figures/rq2_regularity_profile_heatmap.pdf), [`figures/rq2_regularity_profile_heatmap_data.csv`](figures/rq2_regularity_profile_heatmap_data.csv), [`figures/rq2_operational_regularity.metadata.json`](figures/rq2_operational_regularity.metadata.json) |
| `data_inputs` | `data/lake/git_commits.parquet`; `data/lake/git_files.parquet`; `paper_v9/data/metrics/m3_author_activity_participation.csv`; `paper_v9/data/metrics/m3_author_concentration.csv`; `paper_v9/data/metrics/m7_inactivity_trajectory.csv`; `paper_v9/figures/rq2_score_trajectory_base_data.csv` |
| `unit_of_analysis` | equipe-semestre |
| `main_question` | Quão regular é a atividade observável no Git por equipe-semestre, e como esse proxy pode apoiar análises posteriores de heterogeneidade processual? |
| `best_use` | Results/Discussion/Threats como mitigação parcial de heterogeneidade de processo; figura candidata se visualmente clara |
| `key_reading` | Artefato visual e contratual: calcula métricas temporais/autorais de regularidade operacional observável no Git e define, com autorização explícita, um índice composto descritivo em que maior indica atividade mais distribuída. As figuras cruzam esse índice com delta de score, concentração final de commits/clean churn e um heatmap z-scored do perfil operacional. |
| `utility_score` | Alta |
| `limitations` | Regularidade de Git não mede aderência a Scrum/Kanban nem produtividade; semanas/dias sem atividade são zeros apenas dentro do período observado entre primeiro commit e âncora T3; clean churn usa política de paths limpos; o índice composto é descritivo e não uma escala latente validada de processo. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq3_influence_map

| Campo | Valor |
|---|---|
| `artifact_id` | `rq3_influence_map` |
| `artifact_family` | `directional_robustness_sensitivity` |
| `files` | [`figures/rq3_influence_map.png`](figures/rq3_influence_map.png), [`figures/rq3_influence_map.svg`](figures/rq3_influence_map.svg), [`figures/rq3_influence_map.pdf`](figures/rq3_influence_map.pdf), [`figures/rq3_influence_map_data.csv`](figures/rq3_influence_map_data.csv), [`figures/rq3_influence_heatmap_matrix.csv`](figures/rq3_influence_heatmap_matrix.csv), [`figures/rq3_influence_relationship_contract.csv`](figures/rq3_influence_relationship_contract.csv), [`figures/rq3_directional_robustness_summary.csv`](figures/rq3_directional_robustness_summary.csv), [`figures/rq3_influence_map.metadata.json`](figures/rq3_influence_map.metadata.json) |
| `data_inputs` | `paper_v9/data/metrics/m9_leave_one_out_intervals.csv`; `paper_v9/figures/rq2_score_trajectory_base_data.csv`; `paper_v9/figures/rq2_operational_regularity_data.csv`; `paper_v9/data/metrics/m8_rework_magnitude.csv`; `data/lake/evaluator_team_cuts.parquet` |
| `unit_of_analysis` | relação avaliativa × equipe-semestre removida |
| `main_question` | Quais associações direcionais descritivas são mais sensíveis à remoção de uma equipe-semestre específica? |
| `best_use` | Discussion/Threats; diagnóstico de sensibilidade para mitigar amostra pequena e dependência de casos influentes |
| `key_reading` | Artefato de sensibilidade: calcula Spearman rho completo e leave-one-out para relações entre planejamento, score, concentração final, regularidade, complexidade técnica e rework. A figura mostra a variação em rho quando cada equipe-semestre é removida; a matriz do heatmap materializa explicitamente as células usadas pela visualização. O contrato de relações mapeia as 8 categorias da Fase 4.2 para 13 relações operacionais, separando concentração final em commits/clean churn e rework em magnitude/ratio. O resumo de robustez direcional ordena relações pela preservação de sinal e identifica a equipe-semestre mais influente. |
| `utility_score` | Alta |
| `limitations` | Diagnóstico small-n; não é teste confirmatório; mudanças de sinal devem ser descritas como robustez direcional; relações com rework ratio usam apenas casos baseline-eligible; associações observacionais não estabelecem causalidade. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq3_complexity_profile

| Campo | Valor |
|---|---|
| `artifact_id` | `rq3_complexity_profile` |
| `artifact_family` | `complexity_confounding` |
| `files` | [`figures/rq3_complexity_profile_data.csv`](figures/rq3_complexity_profile_data.csv), [`figures/rq3_complexity_metrics_contract.csv`](figures/rq3_complexity_metrics_contract.csv), [`figures/rq3_technical_complexity_vs_rework.png`](figures/rq3_technical_complexity_vs_rework.png), [`figures/rq3_technical_complexity_vs_rework.svg`](figures/rq3_technical_complexity_vs_rework.svg), [`figures/rq3_technical_complexity_vs_rework.pdf`](figures/rq3_technical_complexity_vs_rework.pdf), [`figures/rq3_technical_complexity_vs_rework_data.csv`](figures/rq3_technical_complexity_vs_rework_data.csv), [`figures/rq3_complexity_vs_final_concentration.png`](figures/rq3_complexity_vs_final_concentration.png), [`figures/rq3_complexity_vs_final_concentration.svg`](figures/rq3_complexity_vs_final_concentration.svg), [`figures/rq3_complexity_vs_final_concentration.pdf`](figures/rq3_complexity_vs_final_concentration.pdf), [`figures/rq3_complexity_vs_final_concentration_data.csv`](figures/rq3_complexity_vs_final_concentration_data.csv), [`figures/rq3_planning_rework_complexity_overlay.png`](figures/rq3_planning_rework_complexity_overlay.png), [`figures/rq3_planning_rework_complexity_overlay.svg`](figures/rq3_planning_rework_complexity_overlay.svg), [`figures/rq3_planning_rework_complexity_overlay.pdf`](figures/rq3_planning_rework_complexity_overlay.pdf), [`figures/rq3_planning_rework_complexity_overlay_data.csv`](figures/rq3_planning_rework_complexity_overlay_data.csv), [`figures/rq3_complexity_confounding_summary.csv`](figures/rq3_complexity_confounding_summary.csv), [`figures/rq3_complexity_profile.metadata.json`](figures/rq3_complexity_profile.metadata.json) |
| `data_inputs` | `data/lake/evaluator_team_cuts.parquet`; `data/lake/git_files.parquet`; `paper_v9/data/metrics/m4_churn_magnitude.csv`; `paper_v9/data/metrics/m8_rework_magnitude.csv`; `paper_v9/data/metrics/m6a_structural_planning.csv`; `paper_v9/figures/rq2_score_trajectory_base_data.csv` |
| `unit_of_analysis` | equipe-semestre |
| `main_question` | A complexidade técnica avaliada e a complexidade estrutural inferida do repositório ajudam a contextualizar churn/rework, concentração final e planejamento? |
| `best_use` | Discussion/Threats; base para visualizações e sumários da Fase 5 sobre complexidade como possível confundidor |
| `key_reading` | Artefato contratual, visual e tabular: reúne complexidade técnica avaliada em T1/T2/T3, delta T3-T1, métricas estruturais inferidas de clean paths, churn/rework T3, planejamento T1 e variáveis de trajetória/concentração final. O contrato de métricas separa `evaluated_complexity` de `repository_structural_complexity`, documenta heurísticas de path e registra ausência de classificação manual de arquitetura GenAI. As figuras da Tarefa 5.3 cruzam complexidade técnica T3 com rework, concentração final e planejamento. O sumário da Tarefa 5.4 recalcula associações descritivas com estratificação por mediana de complexidade técnica, registrando `n` por estrato e indisponibilidade quando aplicável. |
| `utility_score` | Alta |
| `limitations` | Complexidade técnica avaliada é dimensão humana do avaliador, não estrutura inferida; métricas estruturais usam heurísticas Git/path e não classificam arquitetura semântica; frontend/backend por path pode subdetectar layouts não convencionais; as figuras são small-n e descritivas; não é modelo causal de ajuste. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq2_score_delta_vs_final7_concentration

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_score_delta_vs_final7_concentration` |
| `artifact_family` | `score_trajectory_concentration` |
| `files` | [`figures/rq2_score_delta_vs_final7_commit_concentration.png`](figures/rq2_score_delta_vs_final7_commit_concentration.png), [`figures/rq2_score_delta_vs_final7_commit_concentration.svg`](figures/rq2_score_delta_vs_final7_commit_concentration.svg), [`figures/rq2_score_delta_vs_final7_commit_concentration.pdf`](figures/rq2_score_delta_vs_final7_commit_concentration.pdf), [`figures/rq2_score_delta_vs_final7_commit_concentration_data.csv`](figures/rq2_score_delta_vs_final7_commit_concentration_data.csv), [`figures/rq2_score_delta_vs_final7_clean_churn_concentration.png`](figures/rq2_score_delta_vs_final7_clean_churn_concentration.png), [`figures/rq2_score_delta_vs_final7_clean_churn_concentration.svg`](figures/rq2_score_delta_vs_final7_clean_churn_concentration.svg), [`figures/rq2_score_delta_vs_final7_clean_churn_concentration.pdf`](figures/rq2_score_delta_vs_final7_clean_churn_concentration.pdf), [`figures/rq2_score_delta_vs_final7_clean_churn_concentration_data.csv`](figures/rq2_score_delta_vs_final7_clean_churn_concentration_data.csv), [`figures/rq2_score_delta_final7_quadrants.csv`](figures/rq2_score_delta_final7_quadrants.csv), [`figures/rq2_score_delta_vs_final7_concentration.metadata.json`](figures/rq2_score_delta_vs_final7_concentration.metadata.json) |
| `data_inputs` | `paper_v9/figures/rq2_score_trajectory_base_data.csv` |
| `unit_of_analysis` | equipe-semestre |
| `main_question` | A concentração de commits ou linhas alteradas nos sete dias finais se associa a melhora, estabilidade ou piora do score avaliativo composto? |
| `best_use` | Results/RQ2 ou Discussion; candidato para diferenciar recuperação tardia de concentração final sem ganho avaliativo |
| `key_reading` | Artefato visual candidato: cruza concentração final de atividade com `delta_score_t3_minus_t1`, colorindo por planejamento repositório-visível e separando semestres por símbolo. A tabela de quadrantes consolida contagens por métrica e tier de planejamento usando mediana de concentração final e threshold de delta da Fase 0. |
| `utility_score` | Alta |
| `limitations` | Associação descritiva com n=14; concentração final não identifica causalidade; delta score usa score composto descritivo; quadrantes usam mediana de concentração e threshold de delta registrado na Fase 0. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq2_planning_concentration_quadrants

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_planning_concentration_quadrants` |
| `artifact_family` | `planning_concentration` |
| `files` | [`figures/rq2_planning_vs_final7_commit_concentration.png`](figures/rq2_planning_vs_final7_commit_concentration.png), [`figures/rq2_planning_vs_final7_commit_concentration.svg`](figures/rq2_planning_vs_final7_commit_concentration.svg), [`figures/rq2_planning_vs_final7_commit_concentration.pdf`](figures/rq2_planning_vs_final7_commit_concentration.pdf), [`figures/rq2_planning_vs_final7_commit_concentration_data.csv`](figures/rq2_planning_vs_final7_commit_concentration_data.csv), [`figures/rq2_planning_vs_final7_clean_churn_concentration.png`](figures/rq2_planning_vs_final7_clean_churn_concentration.png), [`figures/rq2_planning_vs_final7_clean_churn_concentration.svg`](figures/rq2_planning_vs_final7_clean_churn_concentration.svg), [`figures/rq2_planning_vs_final7_clean_churn_concentration.pdf`](figures/rq2_planning_vs_final7_clean_churn_concentration.pdf), [`figures/rq2_planning_vs_final7_clean_churn_concentration_data.csv`](figures/rq2_planning_vs_final7_clean_churn_concentration_data.csv), [`figures/rq2_planning_concentration_quadrant_summary.csv`](figures/rq2_planning_concentration_quadrant_summary.csv), [`figures/rq2_planning_concentration_quadrants.metadata.json`](figures/rq2_planning_concentration_quadrants.metadata.json) |
| `data_inputs` | `paper_v9/figures/rq2_score_trajectory_base_data.csv`; `paper_v9/data/metrics/m8_rework_magnitude.csv` |
| `unit_of_analysis` | equipe-semestre |
| `main_question` | Como o escopo de planejamento repositório-visível em T1 se combina com concentração final de atividade e resultado avaliativo T3? |
| `best_use` | Results/RQ2; figura sintética candidata para conectar planejamento inicial, padrão temporal de trabalho e resultado |
| `key_reading` | Artefato visual candidato: cruza escopo de planejamento repositório-visível com concentração final de commits/clean churn, usando cor para score T3 e tamanho para magnitude absoluta do delta avaliativo. O sumário registra contagens e scores por quadrante. |
| `utility_score` | Alta |
| `limitations` | Planejamento é escopo estrutural observado no repositório, não qualidade semântica; concentração final é proxy temporal; quadrantes são bins descritivos small-n; M8 clean rework entra apenas como proxy de churn por proveniência. |
| `status` | `candidate` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### rq2_student_syndrome_reviewer_response

| Campo | Valor |
|---|---|
| `artifact_id` | `rq2_student_syndrome_reviewer_response` |
| `artifact_family` | `student_syndrome` |
| `files` | [`figures/rq2_student_syndrome_by_evaluator_planning_tier.png`](figures/rq2_student_syndrome_by_evaluator_planning_tier.png), [`figures/rq2_student_syndrome_by_evaluator_planning_tier.svg`](figures/rq2_student_syndrome_by_evaluator_planning_tier.svg), [`figures/rq2_student_syndrome_by_evaluator_planning_tier.pdf`](figures/rq2_student_syndrome_by_evaluator_planning_tier.pdf), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_data.csv`](figures/rq2_student_syndrome_by_evaluator_planning_tier_data.csv), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_summary.csv`](figures/rq2_student_syndrome_by_evaluator_planning_tier_summary.csv), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.png`](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.png), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.svg`](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.svg), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.pdf`](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.pdf), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_data.csv`](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_data.csv), [`figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_summary.csv`](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_summary.csv), [`figures/rq2_student_syndrome_full_period_commits_by_tier.png`](figures/rq2_student_syndrome_full_period_commits_by_tier.png), [`figures/rq2_student_syndrome_full_period_commits_by_tier.svg`](figures/rq2_student_syndrome_full_period_commits_by_tier.svg), [`figures/rq2_student_syndrome_full_period_commits_by_tier.pdf`](figures/rq2_student_syndrome_full_period_commits_by_tier.pdf), [`figures/rq2_student_syndrome_full_period_commits_by_tier_data.csv`](figures/rq2_student_syndrome_full_period_commits_by_tier_data.csv), [`figures/rq2_student_syndrome_full_period_commits_by_tier_summary.csv`](figures/rq2_student_syndrome_full_period_commits_by_tier_summary.csv), [`figures/rq2_student_syndrome_full_period_clean_churn_by_tier.png`](figures/rq2_student_syndrome_full_period_clean_churn_by_tier.png), [`figures/rq2_student_syndrome_full_period_clean_churn_by_tier.svg`](figures/rq2_student_syndrome_full_period_clean_churn_by_tier.svg), [`figures/rq2_student_syndrome_full_period_clean_churn_by_tier.pdf`](figures/rq2_student_syndrome_full_period_clean_churn_by_tier.pdf), [`figures/rq2_student_syndrome_full_period_clean_churn_by_tier_data.csv`](figures/rq2_student_syndrome_full_period_clean_churn_by_tier_data.csv), [`figures/rq2_student_syndrome_full_period_clean_churn_by_tier_summary.csv`](figures/rq2_student_syndrome_full_period_clean_churn_by_tier_summary.csv), [`figures/rq2_student_syndrome_final7_concentration_by_tier.png`](figures/rq2_student_syndrome_final7_concentration_by_tier.png), [`figures/rq2_student_syndrome_final7_concentration_by_tier.svg`](figures/rq2_student_syndrome_final7_concentration_by_tier.svg), [`figures/rq2_student_syndrome_final7_concentration_by_tier.pdf`](figures/rq2_student_syndrome_final7_concentration_by_tier.pdf), [`figures/rq2_student_syndrome_final7_concentration_by_tier_data.csv`](figures/rq2_student_syndrome_final7_concentration_by_tier_data.csv), [`figures/rq2_student_syndrome_final7_concentration_by_tier.metadata.json`](figures/rq2_student_syndrome_final7_concentration_by_tier.metadata.json), [`STUDENT_SYNDROME_REVIEW_RESPONSE.md`](STUDENT_SYNDROME_REVIEW_RESPONSE.md) |
| `data_inputs` | `paper_v9/data/metrics/m3_activity_rolling_7day.csv`; `paper_v9/data/metrics/m4_rolling_7day_trajectory.csv`; `data/lake/git_commits.parquet`; `data/lake/git_files.parquet`; `data/lake/evaluator_team_cuts.parquet`; `paper_v9/data/metrics/m6a_structural_planning.csv`; evaluator-form anchors for 2025.2 and 2026.1 |
| `unit_of_analysis` | equipe-semestre × janela temporal; equipe-semestre para concentração final |
| `main_question` | Como isolar e tornar mensurável a explicação alternativa de “student syndrome” para os picos de atividade próximos ao T3? |
| `best_use` | Response letter; Results/RQ2 ou Discussion se a narrativa precisar explicitar a alternativa de procrastinação |
| `key_reading` | Conjunto de resposta ao revisor: mostra concentração forte no D0 dentro da semana final para ambos os tiers, mas a visão de período completo indica maior dominância final para o tier de menor score/planejamento mais fraco. A figura de concentração final resume a parcela de commits e clean churn pré-T3 que ocorre nos sete dias finais. |
| `utility_score` | Alta |
| `limitations` | Não contém telemetria timestamped de uso de IA; rolling windows se sobrepõem nas trajetórias de período completo; tiers combinam score avaliativo e planejamento repositório-visível; evidência é descritiva e compatível, mas não identificadora causal, de student syndrome. |
| `status` | `response_letter` |
| `superseded_by` | — |
| `last_reviewed` | 2026-09-25 |

### candidate_figure_inventory

| Campo | Valor |
|---|---|
| `artifact_id` | `candidate_figure_inventory` |
| `artifact_family` | `candidate_figures` |
| `files` | [`FIGURES_CANDIDATES_WORKSHOP.md`](FIGURES_CANDIDATES_WORKSHOP.md), [`figures/candidate_rq1_perception_panel.png`](figures/candidate_rq1_perception_panel.png), [`figures/candidate_rq1_perception_panel.svg`](figures/candidate_rq1_perception_panel.svg), [`figures/candidate_rq1_perception_panel.pdf`](figures/candidate_rq1_perception_panel.pdf), [`figures/candidate_rq1_perception_panel_data.csv`](figures/candidate_rq1_perception_panel_data.csv), [`figures/candidate_rq2_temporal_dynamics.png`](figures/candidate_rq2_temporal_dynamics.png), [`figures/candidate_rq2_temporal_dynamics.svg`](figures/candidate_rq2_temporal_dynamics.svg), [`figures/candidate_rq2_temporal_dynamics.pdf`](figures/candidate_rq2_temporal_dynamics.pdf), [`figures/candidate_rq2_temporal_dynamics_data.csv`](figures/candidate_rq2_temporal_dynamics_data.csv), [`figures/candidate_rq3_planning_rework_profile.png`](figures/candidate_rq3_planning_rework_profile.png), [`figures/candidate_rq3_planning_rework_profile.svg`](figures/candidate_rq3_planning_rework_profile.svg), [`figures/candidate_rq3_planning_rework_profile.pdf`](figures/candidate_rq3_planning_rework_profile.pdf), [`figures/candidate_rq3_planning_rework_profile_data.csv`](figures/candidate_rq3_planning_rework_profile_data.csv), [`figures/candidate_rq3_associations_leave_one_out.png`](figures/candidate_rq3_associations_leave_one_out.png), [`figures/candidate_rq3_associations_leave_one_out.svg`](figures/candidate_rq3_associations_leave_one_out.svg), [`figures/candidate_rq3_associations_leave_one_out.pdf`](figures/candidate_rq3_associations_leave_one_out.pdf), [`figures/candidate_rq3_associations_leave_one_out_data.csv`](figures/candidate_rq3_associations_leave_one_out_data.csv) |
| `data_inputs` | Official metric artifacts generated before the robustness-extension phases; see `FIGURES_CANDIDATES_WORKSHOP.md` for per-candidate notes |
| `unit_of_analysis` | Varies by candidate; each candidate preserves its original metric grain and explicit units |
| `main_question` | Quais figuras exploratórias iniciais poderiam apoiar a primeira versão LaTeX sem fechar a seleção editorial? |
| `best_use` | Diagnostic/editorial inventory; consult before selecting main-text or appendix figures |
| `key_reading` | Inventário exploratório com quatro candidatos: RQ1 perception panel, RQ2 temporal dynamics, RQ3 planning/rework profile e RQ3 leave-one-out ranges. Útil para seleção inicial, mas deve ser revisado contra artefatos mais recentes das Fases 1–8 antes de promoção editorial. |
| `utility_score` | Média |
| `limitations` | Algumas figuras foram suplantadas ou refinadas por análises posteriores; os grãos e escalas variam; não deve ser tratado como lista fechada nem como evidência confirmatória. |
| `status` | `diagnostic_only` |
| `superseded_by` | Artefatos específicos das Fases 1–8 quando estes oferecerem leitura mais direta |
| `last_reviewed` | 2026-09-25 |
