# Catálogo versionado de uso dos artefatos — paper_v9

Este catálogo registra o uso editorial e analítico dos artefatos gerados para
o `paper_v9`. Ele deve ser consultado antes de criar novas figuras, tabelas ou
dados derivados, para evitar duplicação e para preservar a memória de decisões
editoriais.

## Status possíveis

- `candidate`: artefato tecnicamente válido, ainda sem decisão editorial final.
- `main_text`: artefato selecionado para o corpo principal.
- `appendix`: artefato adequado para apêndice/suplemento.
- `response_letter`: artefato usado principalmente para responder revisão.
- `diagnostic_only`: artefato útil para decisão interna, mas não recomendado
  como figura/tabela do artigo.
- `superseded`: artefato substituído por outro.
- `discarded`: artefato descartado após revisão.

## Artefatos registrados

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
