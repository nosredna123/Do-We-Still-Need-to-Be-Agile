# Plano de Conversao V8 para V9

## Protocolo de execucao manual

O plano e executado como uma fila de tarefas bloqueadoras. Para cada tarefa,
o agente deve executar somente o escopo declarado, validar os entregaveis,
apresentar resultados e aguardar aprovacao manual explicita. A proxima tarefa
nao pode ser iniciada antes dessa aprovacao, inclusive quando sua dependencia
tecnica ja estiver disponivel.

Cada tarefa deve registrar: objetivo, entradas, alteracoes, artefatos gerados,
comandos de validacao, limitacoes e decisao solicitada ao usuario.

## 1. Objetivo e limites

Este plano produz uma versao v9 reproduzivel do artigo a partir da v8 e das
especificacoes empiricamente testadas em `paper_v9/metricas_v8-analysis/`.

Invariantes do projeto:

- O titulo e as tres questoes de pesquisa da v8 permanecem literalmente
  inalterados.
- `paper_v8/` permanece uma baseline somente leitura. Nenhum artefato v9 deve
  sobrescrever scripts, dados, figuras ou LaTeX v8.
- O resultado v9 usa os contratos de dados e a politica central de artefatos do
  repositorio, incluindo `is_measurement_code_path` e suas whitelist/blacklist.
- Um artefato inexistente, incompleto, com manifesto ausente ou checksum de
  entrada divergente deve ser regenerado; artefatos atuais devem ser retomados
  por padrao (resume).
- Toda afirmacao quantitativa do texto deve apontar para um CSV/Parquet/JSON
  v9, um manifesto de proveniencia e, quando houver LLM, para prompt, payload,
  resposta e evidencia citada versionados.
- Os resultados sao descritivos ou exploratorios. Nenhum script ou texto deve
  inferir causalidade sem desenho que a sustente.
- O artigo, todos os scripts v9, comentarios de codigo, docstrings, manifests,
  nomes de colunas, rotulos de figuras, tabelas, relatorios gerados e mensagens
  de erro devem estar em ingles tecnico internacional, adequado a artigos
  cientificos. Portugues permanece apenas em dados brutos, texto-fonte citado,
  valores observados e, quando necessario, evidencia literal acompanhada de
  traducao/interpretacao em ingles.
- A lingua deve ser validada antes de cada gate editorial; termos metodologicos,
  nomes de metricas e rotulos precisam ser consistentes entre scripts, dados,
  figuras e LaTeX.

## 2. Estrutura de destino

Criar a seguinte estrutura, com `metricas_v8-analysis/` preservado como
especificacao e evidencia de decisao, nao como produtor oficial de dados:

```text
paper_v9/
  V9_CONVERSION_PLAN.md
  metricas_v8-analysis/
  scripts/
    common/
    metrics/
    results/
    llm/
  data/
    metrics/
    results/
    llm/
    manifests/
  figures/
  latex/
    main.tex
    references.bib
    sections/
      methodology.tex
      results.tex
      discussion.tex
      threats_to_validity.tex
      conclusion.tex
      abstract.tex
      introduction.tex
      background_related_work.tex
    tables/
  tests/
```

`paper_v9/data/` e somente esse diretorio recebera dados gerados v9. Cada
produtor persistira um sidecar `<artefato>.metadata.json` contendo pelo menos:

- estado (`success`), versao do contrato e versao da definicao da metrica;
- checksum das entradas, configuracao efetiva e versao do script;
- unidade de analise, chaves, cobertura, ausencias e limitacoes declaradas;
- para LLM: modelo, temperatura, versao do prompt, hash do payload, cache key,
  resposta bruta e referencias de evidencia.

Os scripts usarao escrita atomica (`.partial` seguido de rename) e nao
sobrescreverao artefatos atuais quando o checksum coincidir.

## 3. Tarefas de fundacao

### Tarefa 0.1 - Configurar e validar ambiente LaTeX local

**Objetivo:** garantir que a v9 podera gerar um PDF IEEE correto antes da
conversao de scripts, dados ou texto.

**Escopo:**

1. Detectar `pdflatex`, `latexmk`, `bibtex` ou `biber`, a distribuicao LaTeX e
  a disponibilidade de `IEEEtran.cls`.
2. Instalar somente dependencias ausentes para IEEEtran, bibliografia, tabelas
  e figuras. Se forem necessarios privilegios administrativos, interromper e
  informar o comando para execucao manual do usuario.
3. Criar documento de teste temporario que use IEEEtran, `cite`, `booktabs`,
  `tabularx`, `graphicx`, bibliografia e uma figura local.
4. Compilar por `latexmk` ou sequencia equivalente e verificar PDF, log,
  referencias e citacoes resolvidas.
5. Registrar comandos, versoes e limitacoes em `paper_v9/REPRODUCIBILITY.md`.

**Entregaveis:** comando de compilacao documentado e PDF de teste em
`paper_v9/latex/build/` ou diretorio temporario rastreado.

**Validacao:** compilacao encerra com sucesso, gera PDF legivel e nao contem
erros fatais, figuras ausentes ou referencias bibliograficas nao resolvidas.

**Gate manual:** aprovar o ambiente LaTeX antes da Tarefa 0.2.

### Tarefa 0.2 - Congelar baseline v8 e registrar inventario

**Objetivo:** tornar toda diferenca v8--v9 rastreavel.

**Escopo:** criar manifesto com hashes de LaTeX, scripts, dados, figuras e
notebooks M1--M9; extrair e registrar titulo, RQs e secoes v8 como invariantes;
registrar a reorganizacao existente dos notebooks em `metricas_v8-analysis/`.

**Validacao:** hashes, nove notebooks e invariantes textuais conferem.

**Gate manual:** aprovar baseline antes da Tarefa 1.1.

## 4. Fundacao tecnica e governanca

### Tarefa 1.1 - Criar contrato e utilitarios comuns v9

1. Registrar um manifesto de baseline com hashes de `paper_v8/latex_code`, dos
   scripts v8, dos nove notebooks de analise e dos contratos de entrada.
2. Criar `paper_v9/scripts/common/paths.py`, `provenance.py`, `resume.py` e
   `statistics.py` para resolver diretorios, checksums, escrita atomica,
   manifests e resumos descritivos.
3. Criar `paper_v9/scripts/common/artifact_policy.py` como adaptador para a
   politica central `pipeline_config.is_measurement_code_path`; nao duplicar
   whitelist/blacklist em scripts v9.
4. Criar um comando orquestrador v9 com estagios `metrics`, `results`,
   `figures`, `latex-check` e `all`, todos com resume por padrao e `--force`
   explicito.
5. Criar testes de contrato para chaves, schemas, politica de artefatos,
   manifests, checksum/resume e idempotencia.

**Validacao:** todos os caminhos de entrada/saida resolvem sem tocar em
`paper_v8/`; testes de importacao e sentinelas da politica de artefatos passam.

**Gate manual:** aprovar infraestrutura antes da Tarefa 1.2.

### Tarefa 1.2 - Implementar resume, manifestos e inventario de entradas

1. Declarar em `paper_v9/data/manifests/input_inventory.json` os contratos
   consumidos da raiz do repositorio: lake, analises regeneradas, parent mirrors,
   formularios processados, artefatos de avaliacoes e cache LLM quando aplicavel.
2. Validar as chaves compostas `ID_Equipe, Semestre` onde a unidade e equipe-
   semestre; nunca associar respostas estudantis ou transcricoes a equipes sem
   chave observada.
3. Validar que M4/M8 usam `code-churn-metrics-v2`, `cc-v2-clean-paths` e a
   politica de artefatos vigente; falhar para contratos antigos.
4. Versionar a politica de exclusao observada no manifesto, incluindo `.history/`,
   `backup/`, dependencias, ambientes, build e extensoes fora da allowlist.

**Validacao:** um segundo run sem `--force` reutiliza artefatos atuais; entrada,
configuracao ou sidecar divergente exige regeneracao; M4/M8 rejeitam contratos
antigos.

**Gate manual:** aprovar contratos e resume antes da Tarefa 2.1.

## 4. Implementacao das familias M1--M9

Cada familia tera um script principal em `paper_v9/scripts/metrics/`, dados em
`paper_v9/data/metrics/`, manifesto proprio e teste focal. As nomenclaturas de
saida podem conter subcomponentes (por exemplo, `m4a`), mas cada familia tera um
manifesto agregador `mN_*.manifest.json`.

### Fase 2 - RQ1: M1 e M2

#### M1 - Painel de percepcoes, nao composto de dependencia

Implementar `m1_rq1_perception_panel.py` para produzir indicadores separados
por semestre e marco temporal a partir das familias de perguntas existentes.

- Manter separadas: beneficio percebido de IA, equilibrio declarado de
  autonomia/ferramentas, impacto percebido na carreira e expectativas/desafios
  de projeto.
- Nao chamar a media de familias heterogeneas de dependencia real de IA.
- Relatar cobertura por pergunta, distribuicao, ausencias e mudanca descritiva
  T1--T3 sem inventar painel individual quando o pareamento nao existir.
- Incluir um estado explicito para uso real de IA: `unavailable_not_measured`.

Saidas: painel longo e largo, cobertura, resumo temporal e manifesto M1.

#### M2 - Percepcao de risco/disrupcao por papel

Implementar `m2_role_perception.py` para preservar itens Likert por papel e
escala, sem LLM e sem agregar papeis em um indice unico.

- Reproduzir a estrutura de resposta, cobertura e pares reais de respondentes
  quando identificadores anonimos permitirem pareamento valido.
- Tratar resultados como percepcao de papel, complementar a M1 e nao evidencia
  de uso real de ferramentas.

Saidas: distribuicoes por papel, resumos por corte/semestre, pareamento quando
observado e manifesto M2.

Gate RQ1: M1 e M2 nao fazem alegacao de telemetria de uso. O texto reportara que
o inventario de repositorios nao encontrou rastros fortes versionados de
ferramentas de desenvolvimento com IA; configuracoes locais potencialmente
ignoradas sao limitacao, nao escala de adocao.

### Fase 3 - RQ2: M3, M4 e M5

#### M3 - Dinamica de autoria e atividade

Implementar `m3_author_activity_dynamics.py` usando parent mirrors read-only,
`committer date` e ultimo voto de avaliador como ancora.

- M3a: participacao de commits na fase final.
- M3b: concentracao final de autoria.
- M3c: dinamica/rolling de autoria e atividade em janela de sete dias.
- Manter autoria, concentracao e volume como construtos separados.

#### M4 - Mudanca limpa e trajetoria temporal

Implementar `m4_clean_change_dynamics.py` com a politica central de artefatos.

- M4a: magnitude de churn source/test limpo.
- M4b: intensidade por commit tocante e amplitude de caminhos limpos.
- M4c: composicao de artefatos e filas de revisao de desconhecidos.
- M4d: janela diaria retrospectiva de sete dias, alinhada ao ultimo voto T3,
  para churn limpo e caminhos unicos.
- Nao usar contagem de commits como resultado principal; ela pertence a M3.

#### M5 - Evidencia textual de friccao

Implementar `m5_coordination_evidence.py` inicialmente sem LLM novo.

- Reconstruir um corpus global por marco a partir de chunks tecnicos; chunks nao
  sao observacoes independentes.
- M5a: densidade de marcadores por mil tokens.
- M5b: composicao por alinhamento, repasse, integracao, bloqueio e retrabalho.
- M5c: cobertura de corpus, sessoes de origem e chunks tecnicos.
- Versionar lexico, expor fila auditavel de trechos e proibir correlacao com
  medidas de equipe quando os graos forem incompativeis.

Como extensao opcional posterior, um reprocessamento LLM de M5 devera usar
subtipos estruturados e citacoes literais, nunca uma unica nota opaca por marco.

Gate RQ2: os resultados so comparam temporalmente medidas no mesmo eixo; nao
fazem correlacao entre corpus global M5 e medidas equipe-semestral M3/M4.

### Fase 4 - RQ3: M6, M7, M8 e M9

#### M6 - Planejamento estrutural e conteudo declarativo

Implementar dois produtores coordenados:

- `m6_structural_planning.py` para M6a: presenca, contagem e escopo de
  artefatos de planejamento T1, pela regra deterministica existente.
- `m6_llm_planning_content.py` para M6b: extracao LLM estruturada dos assuntos
  T1, agora autorizada.

O prompt M6b devera retornar JSON validado com:

- `planning_evidence_present`;
- `goals`, `architecture_or_design`, `task_decomposition` e
  `risk_or_dependency`;
- `evidence_quotes` ligadas literalmente ao payload;
- `insufficient_evidence` e motivo de indisponibilidade.

Persistir payloads, respostas, cache, chamadas e uma tabela auditavel por
equipe-semestral. Criar uma revisao humana de amostra estratificada antes de
permitir M6b no texto principal. M6c sera uma matriz de concordancia entre
evidencia estrutural e textual, nunca um score composto.

#### M7 - Dinamica de inatividade de repositorio

Implementar `m7_repository_inactivity.py`.

- M7a: trajetoria diaria de inatividade em janelas retrospectivas de sete dias,
  de -63 a +7 dias do ultimo voto T3.
- M7b: padrao por checkpoints (nunca inativa, apenas T1, intermitente).
- M7c: cobertura de avaliacao T1 entre equipes inativas.
- O rotulo e `repository_inactivity`, nunca `planning_omission`.

#### M8 - Retrabalho limpo com baseline

Implementar `m8_clean_rework.py` usando a mesma politica de M4 e proveniencia
de caminho por primeira aparicao.

- M8a: magnitude de retrabalho limpo em caminhos com baseline T1/T2.
- M8b: participacao de retrabalho limpo no churn T3, condicionada a baseline e
  churn limpo nao nulo.
- M8c: trajetoria diaria de retrabalho limpo em janelas de sete dias, de -21 a
  +7 dias do T3.
- M8d: numero de caminhos limpos preexistentes e elegibilidade de baseline.
- Sempre reportar zeros, cobertura, mediana, total, maximo e participacao do
  maximo; nao chamar proveniencia de caminho de defeito sem validacao semantica.

#### M9 - Associacoes estratificadas

Implementar `m9_structured_associations.py`.

- M9a: M6a versus M8a em todas as 14 equipe-semestrais.
- M9b: M6a versus M8b somente no estrato elegivel para razao de retrabalho.
- M9c: M6a versus desfechos independentes T3 dos avaliadores.
- M9d: M6b versus desfechos somente apos a revisao humana aprovar a qualidade
  do reprocessamento LLM.
- Produzir Spearman descritivo, tabela de cobertura/estratos e intervalo
  leave-one-out. Nao imputar nota 1 para ausencia de Git e nao usar M7 como
  preditor independente.

Gate RQ3: toda associacao declara denominador, estrato, ausencias e influencia
de casos. A conclusao deve permanecer exploratoria mesmo se um coeficiente for
numericamente grande.

## 5. Resultados, visualizacoes e tabelas

### Fase 5 - Catalogo de artefatos de resultados

Implementar em `paper_v9/scripts/results/`:

1. `build_results_summary.py`: gera um JSON unico com numeros aprovados para o
   LaTeX; falha se referencias apontarem para artefatos/metadados ausentes.
2. `build_team_level_table.py`: tabela equipe-semestral com M6a, M6b quando
   aprovado, M7, M8a--d e desfechos; campos indisponiveis permanecem distintos
   de zero.
3. `generate_figures.py`: figuras deterministicas, cada uma com CSV de dados e
   manifesto de figura.
4. `build_evidence_manifest.py`: indice de scripts, dados, figuras, checksums,
   limitacoes e trechos do paper que os consomem.

### Fase 6 - Oficina de selecao de visualizacoes e tabelas

Antes de alterar `results.tex`, realizar uma etapa de decisao com o usuario.
Gerar candidatos, dados subjacentes e vantagens/limites para aprovacao:

| RQ | Candidato | Decisao esperada |
|---|---|---|
| RQ1 | Painel pequeno de indicadores M1 separados e ranking M2 | Selecionar no maximo as vistas que preservem construtos distintos |
| RQ2 | Painel temporal M3/M4d/M5 com eixos/granularidades explicitamente rotulados | Decidir se M5 aparece como anotacao textual, nao serie correlacionada |
| RQ3 | Perfil equipe-semestral de M6a/M8a/M8b/elegibilidade + trajetoria M8c | Escolher tabela principal e figura de distribuicao/influencia |
| RQ3 | Intervalos leave-one-out de M9 | Decidir se entra no corpo ou em apendice/material suplementar |

Nenhuma figura entra no LaTeX antes da aprovacao explicita desta oficina.

Gate 2: cada visualizacao aprovada cabe em um artefato de dados v9 e nao oculta
zero, ausencia, estrato inelegivel ou caso dominante.

## 6. LaTeX modular e revisao editorial

### Fase 7 - Inicializacao modular

1. Copiar a v8 para `paper_v9/latex/` como ponto de partida, preservando titulo,
   RQs, autorias e bibliografia inicialmente.
2. Criar `main.tex` com preambulo, titulo, autores, `\input` das secoes e
   `\bibliography{references}`.
3. Mover conteudo para os oito arquivos de secao definidos na estrutura alvo.
4. Converter tabelas para `latex/tables/` e figuras para referencias relativas
   de `latex/figures/` ou `../figures/`, conforme a configuracao de compilacao
   aprovada.
5. Adicionar comentarios invisiveis de proveniencia para cada numero/figura,
   sem expor jargao de pipeline no texto renderizado.

### Fase 8 - Revisao por secoes, com bloqueio de aprovacao

A ordem e obrigatoria. Uma secao so avanca quando o usuario aprovar a anterior.

1. **Methodology**
   - substituir definicoes M1--M9 por contratos v9;
   - explicitar unidades de analise, politicas de artefatos, LLM M6b, resume e
     limites de grao; preservar RQs literalmente.
   - Gate: metodologia aprovada e todos os numeros/remissoes validos.
2. **Results**
   - atualizar apenas afirmacoes sustentadas por `results_summary.json`,
     tabelas/figuras aprovadas e manifestos;
   - remover afirmações v8 invalidadas: churn bruto, omissao de planejamento,
     friccao constante 8/10, e extremo de 100k linhas como resultado limpo.
   - Gate: resultados aprovados e toda alegacao tem fonte rastreavel.
3. **Discussion**
   - ajustar interpretacao a resultados v9, especialmente heterogeneidade,
     inatividade, retrabalho por baseline e indisponibilidade de telemetria de
     uso de IA.
   - Gate: nenhuma recomendacao de SDD/Agile excede a evidencia.
4. **Threats to Validity**
   - atualizar limites de artefatos Git, classificacao, LLM M6b, corpus M5,
     amostra pequena, influencia e ausencia de rastros de ferramentas.
   - Gate: limites correspondem aos manifests e aos resultados.
5. **Conclusion**
   - reescrever somente apos as quatro secoes anteriores; resumir achados e
     limites sem introduzir evidencia nova.
   - Gate: conclusao aprovada.
6. **Abstract**
   - reescrever exclusivamente a partir do texto aprovado das secoes finais.
   - Gate: resumo aprovado.
7. **Introduction**
   - corrigir motivacao, contribuicoes e linguagem de RQ1 conforme evidencia
     disponivel/indisponivel; titulo e RQs nao mudam.
   - Gate: introducao aprovada.
8. **Background and Related Work**
   - fazer apenas as correcoes necessarias para alinhar termos e reivindicacoes
     metodologicas; referencias novas somente se indispensaveis e verificadas.
   - Gate: texto completo aprovado.

## 7. Verificacao final e entrega

### Fase 9 - Preflight de reproducibilidade

1. Executar todos os scripts v9 duas vezes: primeira geracao e segunda em modo
   resume, verificando que os checksums evitam recomputacao.
2. Executar testes unitarios/contratuais v9 e os testes de politica de artefatos
   compartilhada do repositorio.
3. Verificar manifests, schemas, chaves, valores ausentes, versoes de contrato,
   hashes, figuras e tabelas.
4. Compilar LaTeX quando o ambiente suportar IEEEtran; caso contrario, executar
   verificacoes de `\input`, referencias, citacoes, caminhos de figuras,
   chaves bibliograficas, braces e matematica.
5. Criar `paper_v9/data/manifests/reproducibility_report.json` e
   `paper_v9/REPRODUCIBILITY.md` com comandos, entradas, saídas, versoes e
   limitacoes conhecidas.

### Fase 10 - Revisao manual final

Somente apos todas as secoes receberem aprovacao explicita:

1. Revisar coerencia narrativa entre abstract, RQs, metodo, resultados e
   conclusao.
2. Revisar anonimato, nomes de equipes, dados sensiveis, links e metadados.
3. Ajustar manualmente extensao/paginacao e escolhas finais de figuras para a
   submissao, sem sacrificar rastreabilidade ou qualificadores empiricos.
4. Registrar um changelog v8--v9 com cada afirmacao removida, alterada ou nova
   e o artefato que a sustenta.

## 8. Fila sequencial de tarefas e gates

Cada item requer aprovacao explicita antes do proximo:

1. Tarefa 0.1: configurar e validar ambiente LaTeX/PDF.
2. Tarefa 0.2: congelar baseline v8 e inventario.
3. Tarefa 1.1: criar utilitarios e contrato comum v9.
4. Tarefa 1.2: implementar resume, manifestos e inventario de entradas.
5. Tarefa 2.1: implementar e validar M1.
6. Tarefa 2.2: implementar e validar M2.
7. Tarefa 3.1: implementar e validar M3.
8. Tarefa 3.2: implementar e validar M4.
9. Tarefa 3.3: implementar e validar M5.
10. Tarefa 4.1: implementar e validar M6a.
11. Tarefa 4.2: apresentar protocolo, prompt, custo e amostra de M6b.
12. Tarefa 4.3: executar M6b somente apos aprovacao especifica do protocolo.
13. Tarefa 4.4: implementar e validar M7.
14. Tarefa 4.5: implementar e validar M8.
15. Tarefa 4.6: implementar e validar M9.
16. Tarefa 5.1: gerar catalogo de resultados rastreavel.
17. Tarefa 5.2: gerar candidatos de visualizacao e realizar oficina de escolha.
18. Tarefa 6.1: criar esqueleto LaTeX modular compilavel.
19. Tarefa 7.1: revisar e aprovar Methodology.
20. Tarefa 7.2: revisar e aprovar Results.
21. Tarefa 7.3: revisar e aprovar Discussion.
22. Tarefa 7.4: revisar e aprovar Threats to Validity.
23. Tarefa 7.5: revisar e aprovar Conclusion.
24. Tarefa 7.6: revisar e aprovar Abstract.
25. Tarefa 7.7: revisar e aprovar Introduction.
26. Tarefa 7.8: revisar e aprovar Background and Related Work.
27. Tarefa 8.1: executar preflight de reproducibilidade e compilacao final.
28. Tarefa 8.2: executar revisao final de submissao e changelog v8--v9.

Nao iniciar revisao de LaTeX antes das metricas, dados, manifestos e figuras
aprovados. Nao iniciar uma secao editorial posterior sem aprovacao da secao
anterior. Toda tarefa valida tambem o requisito de ingles internacional para
codigo, artefatos gerados e texto cientifico.