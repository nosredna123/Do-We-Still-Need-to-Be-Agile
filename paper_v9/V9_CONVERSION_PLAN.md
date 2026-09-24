# Plano de Conversão V8 para V9 - Estrutura de Fases e Tarefas

## Protocolo de Execução Manual

O plano é executado como uma **fila de tarefas bloqueadoras**. Para cada tarefa:

1. **Fazer perguntas de esclarecimento** se a tarefa apresentar ambiguidade ou dependência de decisões não registradas
2. **Executar somente o escopo declarado** da tarefa
3. **Validar todos os entregáveis** conforme critérios explícitos
4. **Apresentar resultados** com evidência de sucesso
5. **Aguardar aprovação manual explícita** antes de prosseguir
6. **Registrar cada tarefa** com: objetivo, entrada (input), processamento, saída (output), validação, limitações e decisão

A próxima tarefa **não pode** ser iniciada antes da aprovação, mesmo que sua dependência técnica já esteja disponível.

### Princípios de Engenharia Obrigatórios (Todos os Scripts, Notebooks e Código)

Todo código produzido no plano v9 (scripts de métricas, utilitários comuns, notebooks de verificação, orquestradores) **DEVE** seguir:

1. **DRY (Don't Repeat Yourself)**
   - Nenhuma lógica de resolução de caminhos, hashing, resume, ou política de artefatos duplicada fora de `paper_v9/scripts/common/`
   - Notebooks de verificação devem importar funções dos scripts de métrica, não reimplementar cálculos
   - Constantes compartilhadas (checkpoints T1/T2/T3, chaves compostas, contratos de política) centralizadas em um único módulo

2. **KISS (Keep It Simple, Stupid)**
   - Preferir funções pequenas e diretas a abstrações genéricas não solicitadas
   - Evitar frameworks, classes ou camadas de indireção quando uma função simples resolve
   - Notebooks devem ser lineares e legíveis (célula = um passo de verificação claro), sem "mágica" implícita

3. **Fail Fast**
   - Validar entradas no início de cada função/script; levantar exceção imediatamente se contrato não for satisfeito (chave ausente, schema inválido, contrato de política desatualizado)
   - **Nunca** mascarar dados ausentes ou inválidos com valores default silenciosos (`0`, `""`, `NaN` implícito)
   - Scripts devem abortar com mensagem de erro clara ao primeiro problema, não continuar processamento parcial
   - Notebooks de verificação devem usar `assert` explícitos que interrompem a execução ao primeiro dado inconsistente, em vez de apenas reportar warnings no final

Essas diretrizes se aplicam a **todas** as tarefas de 1.1 em diante e serão verificadas como parte da validação de cada entrega.

### Estrutura de Cada Tarefa

Cada tarefa segue este formato:

```
## Tarefa X.Y - Nome da Tarefa

**Fase:** Nome da Fase  
**Dependências:** Tarefas predecessoras  
**Estimativa:** Tempo aproximado

### Objetivo
Descrição clara do que será entregue.

### Entrada (Input)
- Arquivo/diretório/contrato
- Estrutura esperada
- Validações pré-requisito

### Escopo
1. Item de escopo 1
2. Item de escopo 2
3. ...

### Saída (Output)
- Arquivo 1 (localização, formato, tamanho esperado)
- Arquivo 2
- ...

### Validação
Critérios que confirmam sucesso:
- [ ] Critério 1
- [ ] Critério 2

### Limitações Conhecidas
- Limitação 1
- Limitação 2

### Questões de Esclarecimento (se necessário)
Antes de executar, esclarecer:
- Pergunta 1?
- Pergunta 2?

### Gate
**Status esperado ao completar:** APROVADO para próxima tarefa
```

## Protocolo Obrigatório de Validação com Dados V8

**Antes de qualquer nova tarefa de métrica (2.1+), é OBRIGATÓRIO:**

1. **Analisar dados e código-fonte v8**
   - Ler análises existentes em `paper_v9/metricas_v8-analysis/` (se disponível) ou `paper_v8/` (notebooks exploratórios)
   - Entender **exatamente** como a métrica foi calculada em v8 (fórmula, tratamento de casos extremos, exclusões)
   - Identificar casos reais nos dados v8 que exemplifiquem a métrica
   - Documentar quaisquer ambiguidades ou suposições em v8 que v9 deve resolver
   - Se a análise v8, os dados ou o código não permitirem determinar com segurança uma regra, unidade, mapeamento temporal, rubrica ou tratamento de ausência, interromper a implementação desse ponto e registrar perguntas de esclarecimento antes de escolher uma convenção

2. **Esclarecer gaps antes de implementar**
   - Se o código v8 ou documentação estiverem incompletos ou ambíguos, registrar questões de esclarecimento
   - Pedir aprovação explícita de como v9 diferirá de v8 (se aplicável)
   - Confirmar que a unidade de análise (equipe-semestre vs. corpus global) está clara
   - Criar uma matriz de rastreabilidade para cada métrica: recomendação da análise v8, decisão v9, artefato/célula que a evidencia, estado (`applied`, `partially_applied`, `not_applied`, `not_applicable`) e justificativa
   - Nenhuma recomendação da análise v8 pode desaparecer por omissão silenciosa; pendências devem bloquear o gate ou ter decisão explícita aprovada
   - A seção `Questões de Esclarecimento` deve ser preenchida para cada ambiguidade material; a tarefa só pode prosseguir nesse ponto após resposta/aprovação explícita ou decisão documentada de escopo

3. **Gerar notebook de verificação v9**
   - Para cada métrica M1–M9, criar notebook em `paper_v9/verification_notebooks/verify_m{N}.ipynb`
   - Notebook deve:
     - Carregar dados brutos e processados (CSV da métrica)
     - Validar tipos de dados, ranges esperados, ausências
     - Comparar resumos (média, mediana, std) com v8 onde aplicável
     - Plotar distribuições, trajetórias, padrões por team-semestre
     - Executar testes de sanidade: nenhum valor impossível, cobertura declarada, sem NaN silencioso
     - Apontar outliers, gaps e exceções com justificativas
     - **Falhar explicitamente** se os dados não forem válidos
   - Demonstrar os artefatos produzidos: exibir amostras das tabelas/CSV e as figuras geradas no próprio notebook
   - Exportar e exibir figuras em formatos exploratórios e article-ready quando o backend permitir (HTML interativo e PDF/SVG/PNG)
   - Produzir uma análise preliminar, descritiva e explicitamente não causal de como a métrica contribui para o RQ vinculado
   - Separar claramente validação, demonstração de artefatos e interpretação exploratória; não transformar a análise preliminar em conclusão do artigo
   - Notebook deve ser executável end-to-end (sem interrupções, sem passos manuais)

4. **Validar contra dados reais antes de usar em artigo**
   - Executar `pytest` dos testes de métrica
   - Executar notebook de verificação
   - Revisar manualmente ao menos 2–3 equipe-semestrais em detalhe (rastrear dados brutos → entrada → saída)
   - Registrar desvios de v8 e justificativa

### Estrutura de Validação por Métrica

Para cada métrica M1–M9, criar 3 artefatos **antes** de usar dados em artigo:

| Artefato | Localização | Responsabilidade |
|----------|-----------|-----------------|
| Análise V8 | `paper_v9/metricas_v8-analysis/analyze_m{N}.md` ou notebook v8 | Ler, resumir, identificar ambiguidades |
| Script de Métrica | `paper_v9/scripts/metrics/m{N}_*.py` | Implementar conforme v8, com correções aprovadas |
| Notebook de Verificação e Análise Preliminar | `paper_v9/verification_notebooks/verify_m{N}.ipynb` | Validar outputs, comparar com v8, demonstrar tabelas/figuras, analisar preliminarmente o RQ e apontar desvios |

### Auditoria obrigatória de transformação V8--V9

Antes de aprovar qualquer tarefa de métrica, o notebook e a análise da métrica
devem apresentar uma tabela de rastreabilidade com, no mínimo:

| Campo | Conteúdo obrigatório |
|---|---|
| `v8_recommendation` | Formulação literal ou paráfrase verificável da recomendação v8 |
| `v9_decision` | Como a recomendação foi implementada, alterada ou rejeitada |
| `status` | `applied`, `partially_applied`, `not_applied` ou `not_applicable` |
| `evidence` | Arquivo, coluna, teste ou célula que demonstra o estado |
| `limitation_or_approval` | Pendência, justificativa e aprovação necessária quando não aplicada |

O gate da métrica só pode ser `APPROVED` quando todas as recomendações
obrigatórias estiverem `applied` ou quando cada exceção tiver uma decisão
explícita registrada e aprovada. Reutilizar um artefato v8 sem executar a
transformação recomendada deve ser marcado como `not_applied`, mesmo que o
artefato seja aritmeticamente correto.

### Padrão obrigatório dos notebooks de verificação

Embora o nome `verify_m{N}.ipynb` seja preservado para estabilidade do contrato,
cada notebook deve cumprir três papéis em células claramente separadas:

1. **Verification:** carregar os artefatos produzidos, validar schemas, tipos,
   ranges, ausências, cobertura, invariantes e comparação com v8 quando
   aplicável; qualquer inconsistência deve interromper a execução com `assert`
   ou exceção explícita.
2. **Artifact demo:** exibir amostras de tabelas e figuras geradas, incluindo
   links ou renderização dos formatos interativos e versões article-ready. A
   demonstração deve consumir os artefatos oficiais, sem recalcular a métrica
   em uma implementação paralela.
3. **Preliminary RQ analysis:** produzir resumos e diferenças descritivas que
   mostrem como a métrica pode informar o RQ vinculado. A célula deve declarar
   unidade de análise, limitações, ausência de causalidade e estados
   `unavailable_not_measured`; não deve introduzir afirmações novas sem fonte.

Cada notebook novo deve ser executado integralmente no ambiente do projeto
antes de a tarefa ser considerada concluída. A validação deve registrar que
todas as células executaram, que as figuras foram efetivamente materializadas
e que os artefatos demonstrados existem e não estão vazios.

---

## Status das Tarefas de Fundação

✓ **Tarefa 0.1 CONCLUÍDA** (2026-09-24)  
Validação do ambiente LaTeX: pdfTeX, BibTeX, IEEEtran.cls instalados. PDF de teste gerado. Documentação em REPRODUCIBILITY.md.

✓ **Tarefa 0.2 CONCLUÍDA** (2026-09-24)  
Congelamento de baseline v8: título e RQs registrados como invariantes, todos 9 métricas (M1–M9) hashadas, LaTeX e figuras congeladas em SHA256.

✓ **Tarefa 1.1 CONCLUÍDA** (2026-09-24)  
Infraestrutura comum v9 criada: `paths.py`, `provenance.py`, `resume.py`, `statistics.py`, `artifact_policy.py` (todos reaproveitando `pipeline_core`/`pipeline_config`, sem duplicar lógica), orquestrador `orchestrate_v9.py` com stages `metrics/results/figures/latex-check/all`, e suite `test_contracts.py` com 13 testes (100% passando). Suite completa do repositório (273 passed, 6 skipped) permanece verde. Documentado em `INFRASTRUCTURE.md`.

✓ **Tarefa 1.2 CONCLUÍDA** (2026-09-24)  
`input_inventory.json` gerado a partir de dados reais (`build_input_inventory.py`): 7 contratos do lake hashados (sha256 real), 14 team-semesters validados contra `git_repository_snapshots` como referência canônica, 9 lacunas de checkpoint documentadas (idênticas ao `lake_validation_report.json`), gap de transcripts 2026.1 registrado explicitamente. `validate_keys.py` valida chaves compostas e rejeita contratos `code-churn-metrics` desatualizados (fail-fast). `test_input_contracts.py` com 14 testes (unitários sintéticos + integração contra dados reais), 100% passando. Suite completa (287 passed, 6 skipped) permanece verde. Documentado em `INPUTS_SUMMARY.md`.

---

## Checklist de Execução do Plano V9

### Fase 0: Fundação (Concluída)
- [x] 0.1 - Configurar e validar ambiente LaTeX local
- [x] 0.2 - Congelar baseline v8 e registrar inventário

### Fase 1: Infraestrutura Técnica e Governança
- [x] 1.1 - Criar contrato e utilitários comuns v9
- [x] 1.2 - Implementar resume, manifestos e inventário de entradas

### Fase 2: RQ1 - Percepção e Adoção de IA
- [x] 2.1 - Implementar e validar M1 (Painel de Percepções) — aprovado em 2026-09-24 para escopo descritivo M1 v2
- [x] 2.2 - Implementar e validar M2 (Percepção de Risco por Papel) — aprovado em 2026-09-24 para escopo descritivo

### Fase 3: RQ2 - Dinâmica de Repositório e Fricção de Coordenação
- [x] 3.1 - Implementar e validar M3 (Dinâmica de Autoria e Atividade) — aprovado em 2026-09-24 para escopo descritivo M3a-M3c
- [x] 3.2 - Implementar e validar M4 (Mudança Limpa e Trajetória Temporal) — aprovado em 2026-09-24 para escopo descritivo M4a-M4d
- [x] 3.3 - Implementar e validar M5 (Evidência Textual de Fricção) — aprovado em 2026-09-24 para escopo determinístico descritivo

### Fase 4: RQ3 - Planejamento, Retrabalho e Associações
- [x] 4.1 - Implementar e validar M6a (Planejamento Estrutural) — aprovado em 2026-09-24 para escopo estrutural determinístico
- [x] 4.2 - Apresentar protocolo, prompt, custo e amostra de M6b (Análise LLM de Planejamento) — aprovado em 2026-09-24 para execução controlada
- [x] 4.3 - Executar M6b após aprovação específica do protocolo — aprovado em 2026-09-24; nove casos observados, cinco indisponíveis, campos estruturados propagados separadamente
- [ ] 4.4 - Implementar e validar M7 (Dinâmica de Inatividade de Repositório) — implementação técnica concluída; aprovação manual pendente
- [ ] 4.5 - Implementar e validar M8 (Retrabalho Limpo com Baseline) — implementação técnica concluída; aprovação manual pendente
- [ ] 4.6 - Implementar e validar M9 (Associações Estratificadas) — implementação técnica concluída; aprovação manual pendente

### Fase 5: Resultados e Visualizações
- [ ] 5.1 - Gerar catálogo de artefatos de resultados
- [ ] 5.2 - Gerar candidatos de visualização e realizar oficina de escolha

### Fase 6: Preparação LaTeX
- [ ] 6.1 - Criar esqueleto LaTeX modular compilável

### Fase 7: Revisão Editorial (Ordem Obrigatória)
- [ ] 7.1 - Revisar e aprovar Methodology
- [ ] 7.2 - Revisar e aprovar Results
- [ ] 7.3 - Revisar e aprovar Discussion
- [ ] 7.4 - Revisar e aprovar Threats to Validity
- [ ] 7.5 - Revisar e aprovar Conclusion
- [ ] 7.6 - Revisar e aprovar Abstract
- [ ] 7.7 - Revisar e aprovar Introduction
- [ ] 7.8 - Revisar e aprovar Background and Related Work

### Fase 8: Verificação Final e Entrega
- [ ] 8.1 - Executar preflight de reproducibilidade e compilação final
- [ ] 8.2 - Executar revisão final de submissão e changelog v8–v9

**Progresso Total:** 14/28 tarefas concluídas (50%)
**Tarefas técnicas concluídas:** 4.4 (M7 gerado; gate manual pendente), 4.5 (M8 gerado; gate manual pendente) e 4.6 (M9 gerado; gate manual pendente)

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

---

# FASES DETALHADAS DO PLANO V9

## Fase 1: Infraestrutura Técnica e Governança

Objetivo: Estabelecer utilitários comuns, contratos de dados, e policies compartilhadas que sustentarão todas as implementações de métricas (M1–M9).

### Tarefa 1.1 - Criar Contrato e Utilitários Comuns V9

**Dependências:** 0.1 ✓, 0.2 ✓  
**Estimativa:** 3–4 horas  
**Prioridade:** CRÍTICA (bloqueador de todas as métricas)

#### Objetivo
Estabelecer infraestrutura reutilizável para caminhos, manifests, checksums, escrita atômica, políticas de artefatos e orquestração de v9.

#### Entrada (Input)
- `paper_v9/data/manifests/v8_baseline_manifest.json` (manifest baseline congelado de 0.2)
- `pipeline_config.is_measurement_code_path` (política central de artefatos do repositório)
- Estrutura de diretórios v9 criada em 0.1/0.2

#### Escopo

1. **Criar `paper_v9/scripts/common/paths.py`**
   - Função `resolve_data_dir()` → retorna caminho absoluto de `paper_v9/data/`
   - Função `resolve_metrics_dir()` → retorna `paper_v9/data/metrics/`
   - Função `resolve_results_dir()` → retorna `paper_v9/data/results/`
   - Função `resolve_scripts_dir()` → retorna `paper_v9/scripts/`
   - Testes unitários para cada função
   - **Nenhum caminho absoluto codificado; tudo relativo ao workspace root**

2. **Criar `paper_v9/scripts/common/provenance.py`**
   - Classe `FileHash` com métodos:
     - `compute_sha256(filepath) → str`
     - `verify_hash(filepath, expected_hash) → bool`
     - `write_hash_sidecar(artifact_path, computed_hash) → sidecar_path`
   - Suporte para `.metadata.json` sidecar com schema definido
   - Testes de idempotência (mesmo arquivo = mesmo hash)

3. **Criar `paper_v9/scripts/common/resume.py`**
   - Classe `ArtifactCache` com métodos:
     - `should_regenerate(artifact_path, input_hash, config_hash) → bool`
     - `mark_complete(artifact_path) → None`
     - `clear_cache(artifact_path) → None`
   - Lógica: regenerar se faltam metadata, hashes divergem, ou `--force` ativado
   - Resumo por padrão; `--force` força recomputação

4. **Criar `paper_v9/scripts/common/statistics.py`**
   - Funções para sumários descritivos (median, mean, std, min, max, percentiles)
   - Nenhuma inferência causal; apenas estatísticas exploratórias
   - Retorna dicts estruturados (não strings formatadas)

5. **Criar `paper_v9/scripts/common/artifact_policy.py`**
   - Importa `pipeline_config.is_measurement_code_path`
   - Fornece interface única: `is_clean_path(filepath, policy_version) → bool`
   - **Não duplicar whitelist/blacklist; apenas adaptar**
   - Testes contra `code-churn-metrics-v2` policy

6. **Criar orquestrador v9: `paper_v9/scripts/orchestrate_v9.py`**
   - CLI com subcomandos: `metrics`, `results`, `figures`, `latex-check`, `all`
   - Flag `--force` para desabilitar resume
   - Flag `--verbose` para debug output
   - Retorna status JSON com artifacts gerados e hashes

7. **Criar suite de testes de contrato: `paper_v9/tests/test_contracts.py`**
   - Testes de importação de todos os módulos comuns
   - Testes de validade de chaves compostas (`ID_Equipe, Semestre`)
   - Testes de política de artefatos
   - Testes de manifests (schemas, checksums)
   - Testes de idempotência (run 2× = mesmos hashes)

#### Saída (Output)
- `paper_v9/scripts/common/paths.py` (~150 linhas, 100% testadas)
- `paper_v9/scripts/common/provenance.py` (~200 linhas, 100% testadas)
- `paper_v9/scripts/common/resume.py` (~150 linhas, 100% testadas)
- `paper_v9/scripts/common/statistics.py` (~100 linhas, 100% testadas)
- `paper_v9/scripts/common/artifact_policy.py` (~80 linhas, 100% testadas)
- `paper_v9/scripts/orchestrate_v9.py` (~250 linhas, CLI funcional)
- `paper_v9/tests/test_contracts.py` (~300 linhas, todos os testes passam)
- `paper_v9/scripts/common/__init__.py` (importa todos os módulos)
- `paper_v9/INFRASTRUCTURE.md` (documentação de uso dos módulos comuns)

#### Validação
- [ ] Todos os imports funcionam: `from paper_v9.scripts.common import paths, provenance, resume, statistics, artifact_policy`
- [ ] `pytest paper_v9/tests/test_contracts.py -v` passa 100%
- [ ] `python paper_v9/scripts/orchestrate_v9.py --help` funciona
- [ ] Nenhum caminho absoluto em `paper_v9/scripts/common/*.py`
- [ ] Arquivo `.metadata.json` é criado com schema válido após primeiro artifact
- [ ] Segunda execução sem `--force` reutiliza artifact (resume = True)
- [ ] Todos os logs e mensagens de erro em **inglês técnico internacional**

#### Limitações Conhecidas
- tlmgr em modo user está desabilitado no sistema (não afeta v9 scripts)
- Whitelist de artefatos pode estar desatualizada se `pipeline_config` for modificado externamente

#### Questões de Esclarecimento
Antes de executar, esclarecer:
1. **Versão de Python esperada?** (assumindo 3.11.15 do .venv)
2. **Todos os scripts common devem ter docstrings e type hints?** (assumindo sim)
3. **Namespace para imports: `paper_v9.scripts.common` ou `v9.scripts.common`?** (assumindo anterior)

#### Gate
**Status ao completar:** ✓ APROVADO para Tarefa 1.2

---

### Tarefa 1.2 - Implementar Resume, Manifestos e Inventário de Entradas

**Dependências:** 1.1 ✓  
**Estimativa:** 2–3 horas  
**Prioridade:** ALTA (bloqueia todas as métricas)

#### Objetivo
Estabelecer contrato de entrada, validar chaves compostas (ID_Equipe, Semestre), definir inventário de fontes de dados que alimentarão M1–M9, e documentar política de exclusão de artefatos.

#### Entrada (Input)
- `paper_v9/scripts/common/` (infraestrutura de 1.1)
- `pipeline_config.is_measurement_code_path` (policy central)
- Datasets de raiz do repo: lake, git mirrors, formulários processados, transcripts, avaliações
- V8 baseline manifest (`v8_baseline_manifest.json`)

#### Escopo

1. **Criar `paper_v9/data/manifests/input_inventory.json`**
   - Declarar todas as fontes de dados consumidas:
     - Lake (data/lake/): estrutura, schemas, versão do contrato
     - Git parent mirrors (data/raw/repos_parent_cache/): política read-only
     - Formulários processados (data/processed/surveys/): checksum esperado
     - Transcripts (data/processed/transcripts/): cobertura por sessão/semestre
     - Avaliações de projeto (data/processed/evaluations/): checksum de hashes de equipes
   - Versionar cada entrada: contrato_version, data_hash, timestamp
   - Exemplo para M4/M8: referenciar `code-churn-metrics-v2`, `cc-v2-clean-paths`

2. **Validar chaves compostas `(ID_Equipe, Semestre)`**
   - Criar script `paper_v9/scripts/common/validate_keys.py`
   - Garantir que nunca associamos respostas estudantis ou transcripts a equipes sem chave observada
   - Testar contra todas as 14 equipe-semestrais
   - Gerar relatório de cobertura por checkpoint (T1, T2, T3)

3. **Definir exclusões de artefatos (`.history/`, `backup/`, etc.)**
   - Registrar whitelist de diretórios analisados
   - Registrar blacklist de padrões a descartar: `.git/`, `node_modules/`, `.env`, etc.
   - Versionar política em `input_inventory.json`
   - Testar contra 1–2 repositórios reais

4. **Verificar validade de M4/M8 contratos**
   - Confirmar que inputs para M4/M8 usam `code-churn-metrics-v2`
   - Confirmar que `cc-v2-clean-paths` está presente
   - Falhar se versão de contrato anterior for detectada
   - Gerar `input_inventory.json` com políticas vigentes

5. **Criar resumo de inventário: `paper_v9/INPUTS_SUMMARY.md`**
   - Lista todas as fontes de dados
   - Registra checksums esperados
   - Documenta coberturas por team-semestre
   - Referencia v8 baseline para comparação

#### Saída (Output)
- `paper_v9/data/manifests/input_inventory.json` (~100–200 linhas, validação JSON rigorosa)
- `paper_v9/scripts/common/validate_keys.py` (~150 linhas, 100% testado)
- `paper_v9/INPUTS_SUMMARY.md` (2–3 KB, narrativa clara)
- `paper_v9/tests/test_input_contracts.py` (~200 linhas, cobertura de chaves e exclusões)

#### Validação
- [ ] `input_inventory.json` valida como JSON bem-formado
- [ ] Todos os 14 team-semesters têm chaves `(ID_Equipe, Semestre)` no lake
- [ ] `pytest paper_v9/tests/test_input_contracts.py -v` passa 100%
- [ ] M4/M8 rejeitam contratos antigos (codigo-churn-metrics-v1, etc.)
- [ ] Whitelist/blacklist testados contra 2+ repositórios reais
- [ ] Relatório de cobertura T1/T2/T3 sem lacunas críticas

#### Limitações Conhecidas
- Alguns team-semesters podem ter gaps temporários em transcripts (não invalidar, apenas documentar)
- Política de exclusão pode evoluir; manifest versionado permite retrospecção

#### Questões de Esclarecimento
Antes de executar, esclarecer:
1. **Qual é o formato exato de chaves de team-semestre no lake?** (p. ex., `extensao3-2025_2-team_02`)
2. **Qual versão mínima de code-churn-metrics é aceitável para M4/M8?** (assumindo v2 única)
3. **Gaps em transcripts (p. ex., sessão 3 faltando) devem bloquear ou apenas documentar?** (assumindo documentar)

#### Gate
**Status ao completar:** ✓ APROVADO para Fase 2 (M1–M2)

---



## Fase 2: RQ1 - Percepção e Adoção de IA

Objetivo: Implementar as métricas que descrevem como estudantes desenvolvadores utilizam IA generativa e como isso molda suas percepções longitudinais sobre papéis de engenharia de software e expectativas de projeto.

### Tarefa 2.1 - Implementar e Validar M1 (Painel de Percepções)

**Dependências:** 1.2 ✓  
**Estimativa:** 2–3 horas (análise v8) + 2–3 horas (implementação) + 1–2 horas (verificação)  
**Métrica RQ:** RQ1  

#### Pré-Requisito Obrigatório: Análise V8
Antes de implementar, **DEVE**:
1. Ler e resumir `paper_v8/` (análise de M1, fórmulas, tratamento de dados)
2. Identificar e registrar em `paper_v9/metricas_v8-analysis/analyze_m1.md`:
   - Como M1 foi calculada em v8 (itens Likert, agregação, familias)
   - Quais familias de percepção foram mantidas separadas
   - Quaisquer exclusões, transformações ou ajustes aplicados
   - Exemplos concretos de 2–3 equipe-semestrais (valores brutos → resultado final)
   - Ambiguidades ou gaps no código/documentação v8
3. Pedir esclarecimento sobre desvios v9 desejados (se houver)

#### Objetivo
Produzir indicadores separados de percepção (não compostos) por semestre e marco temporal, preservando as distinções entre benefício percebido de IA, equilíbrio autonomia/ferramentas, impacto na carreira e expectativas/desafios de projeto.

#### Entrada (Input)
- Survey responses (data/processed/surveys/) para T1, T2, T3
- Questões de percepção mapeadas: familias de itens Likert
- Input inventory e validação de chaves (Tarefa 1.2)
- **Análise v8 registrada em `paper_v9/metricas_v8-analysis/analyze_m1.md`**

#### Escopo
1. Criar `paper_v9/scripts/metrics/m1_rq1_perception_panel.py`
2. Extrair famílias de percepção: AI benefit, autonomy/tool balance, career impact, project expectations
3. Manter separados (não agregar em índice único)
4. Reportar cobertura por pergunta, distribuição, ausências, mudança descritiva T1–T3
5. Declarar `unavailable_not_measured` explicitamente onde dados faltam
6. Gerar CSV longo e CSV largo (wide format para tabelas)
7. Criar manifesto `m1_rq1_perception_panel.metadata.json`
8. **Validar contra dados v8: comparar resumos estatísticos, distribuições, coberturas**
9. Extrair os campos brutos de uso autorreportado por `Semestre × temporal_marker`: frequência geral, frequência em projetos, tarefas, ferramentas e experiência prévia
10. Produzir uma distribuição separada para equilíbrio autonomia/ferramentas
11. Produzir codificação exploratória auditável dos temas de impacto de carreira, bloqueada para uso confirmatório até validação humana

#### Saída (Output)
- `paper_v9/metricas_v8-analysis/analyze_m1.md` (~2–3 KB, resumo de v8)
- `paper_v9/data/metrics/m1_rq1_perception_panel_long.csv` (structure: team_semester, checkpoint, perception_family, mean, std, n, coverage)
- `paper_v9/data/metrics/m1_rq1_perception_panel_wide.csv`
- `paper_v9/data/metrics/m1_rq1_usage_frequency.csv`
- `paper_v9/data/metrics/m1_rq1_usage_tasks.csv`
- `paper_v9/data/metrics/m1_rq1_usage_tools.csv`
- `paper_v9/data/metrics/m1_rq1_prior_ai_project_experience.csv`
- `paper_v9/data/metrics/m1_rq1_autonomy_tool_balance.csv`
- `paper_v9/data/metrics/m1_rq1_career_impact_topics_exploratory.csv`
- `paper_v9/data/metrics/m1_rq1_perception_distribution.csv`
- `paper_v9/data/metrics/m1_rq1_perception_panel.metadata.json` (checksum, coverage summary)
- `paper_v9/scripts/metrics/m1_rq1_perception_panel.py` (testado)
- **`paper_v9/verification_notebooks/verify_m1.ipynb`** (validação de dados, comparação com v8)

#### Validação
- [ ] Análise v8 completa e registrada em `analyze_m1.md`
- [ ] Matriz de rastreabilidade de todas as recomendações da análise v8 preenchida, com nenhuma pendência omitida
- [ ] M1 CSV válidos e bem-formados
- [ ] Nenhuma média de famílias heterogêneas
- [ ] Uso autorreportado extraído separadamente de percepções e com proveniência temporal
- [ ] Codificação de carreira marcada como exploratória até validação humana
- [ ] `unavailable_not_measured` declarado onde apropriado
- [ ] Notebook `verify_m1.ipynb` executa end-to-end sem erros
- [ ] Notebook valida tipos, ranges, distribuições
- [ ] Notebook compara resumos com v8 (médias, medianas, std)
- [ ] Segunda execução sem `--force` reutiliza (checksum match)
- [ ] Cobertura T1/T2/T3 documentada; sem lacunas inesperadas
- [ ] Pelo menos 2–3 equipe-semestrais validadas manualmente

#### Limitações Conhecidas
- Alguns respondentes podem ter pulado questões (registrar como ausência)
- Não agregar percepções heterogêneas (falhar se scripts tentarem)

#### Gate
**Status ao completar:** ✓ APROVADO para Tarefa 2.2

---

### Tarefa 2.2 - Implementar e Validar M2 (Percepção de Risco por Papel)

**Dependências:** 2.1 ✓  
**Estimativa:** 2–3 horas  
**Métrica RQ:** RQ1  

#### Objetivo
Preservar itens Likert por papel de projeto e escala, tratando resultados como perceção de papel (complementa M1), não como evidência de uso real de ferramentas.

#### Entrada (Input)
- Survey responses (data/processed/surveys/) com role attribution
- Input inventory e validação de chaves (Tarefa 1.2)

#### Escopo
1. Criar `paper_v9/scripts/metrics/m2_role_perception.py`
2. Extrair percepção de risco/disrupção por papel (developer, architect, QA, etc.)
3. Preservar estrutura de respostas, sem agregar papéis em índice único
4. Reportar distribuições por papel, resumos por corte/semestre, pareamento T1–T3 quando observado
5. Criar manifesto com cobertura por papel
6. Criar `paper_v9/metricas_v8-analysis/analyze_m2.md` com matriz V8→V9 e limitações

#### Saída (Output)
- `paper_v9/data/metrics/m2_role_perception_distributions.csv`
- `paper_v9/data/metrics/m2_role_perception_by_team_semester.csv`
- `paper_v9/data/metrics/m2_role_perception_paired_t1_t3.csv`
- `paper_v9/data/metrics/m2_role_perception.metadata.json`
- `paper_v9/scripts/metrics/m2_role_perception.py` (testado)
- `paper_v9/verification_notebooks/verify_m2.ipynb` (executado end-to-end)

#### Validação
- [ ] Papéis mantidos separados (não agregados)
- [ ] Pareamento real de respondentes documentado
- [ ] Cobertura por papel-semestre clara
- [ ] Pareamento T1–T3 reportado sem expor identificadores
- [ ] M2 descrito como percepção de disrupção, não risco objetivo ou uso real
- [ ] Matriz V8→V9 registrada em `analyze_m2.md`
- [ ] Notebook verifica, demonstra artefatos e analisa preliminarmente RQ1
- [ ] Segunda execução sem `--force` reutiliza (checksum match)

#### Gate
**Status ao completar:** ✓ APROVADO para Fase 3 (M3–M5)

---

## Fase 3: RQ2 - Dinâmica de Repositório e Fricção de Coordenação

Objetivo: Implementar métricas que contrastam densidade temporal de atividade de repositório com tipificação qualitativa de fricção de coordenação humana ao longo do ciclo de vida do projeto.

### Tarefa 3.1 - Implementar e Validar M3 (Dinâmica de Autoria e Atividade)

**Dependências:** 1.2 ✓  
**Estimativa:** 3–4 horas  
**Métrica RQ:** RQ2  

#### Objetivo
Capturar dinâmica de autoria e atividade usando parent mirrors read-only, data de committer e último voto de avaliador como âncora.

#### Entrada (Input)
- Git parent mirrors (data/raw/repos_parent_cache/) — read-only
- Avaliações (data/processed/evaluations/) para T3 anchor
- Input inventory (Tarefa 1.2)

#### Escopo
1. Criar `paper_v9/scripts/metrics/m3_author_activity_dynamics.py`
2. M3a: participação de commits na fase final (T2–T3)
3. M3b: concentração final de autoria (Herfindahl-Hirschman ou similar)
4. M3c: dinâmica/rolling de autoria e atividade em janela de 7 dias
5. Manter autoria, concentração e volume como construtos separados
6. Usar T3 evaluator vote como âncora temporal

#### Saída (Output)
- `paper_v9/data/metrics/m3_author_activity_participation.csv`
- `paper_v9/data/metrics/m3_author_concentration.csv`
- `paper_v9/data/metrics/m3_activity_rolling_7day.csv`
- `paper_v9/data/metrics/m3_activity_rolling_7day_pooled.csv`
- `paper_v9/data/metrics/m3_author_activity_dynamics.metadata.json`
- `paper_v9/scripts/metrics/m3_author_activity_dynamics.py` (testado)

#### Validação
- [ ] Autoria, concentração e volume tratados como construtos separados
- [ ] Janelas de 7 dias alinhadas corretamente
- [ ] Todas as 14 equipe-semestrais cobertas
- [ ] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** ✓ APROVADO para Tarefa 3.2

---

### Tarefa 3.2 - Implementar e Validar M4 (Mudança Limpa e Trajetória Temporal)

**Dependências:** 1.2 ✓ (especialmente validação code-churn-metrics-v2)  
**Estimativa:** 4–5 horas  
**Métrica RQ:** RQ2  

#### Objetivo
Medir magnitude e trajetória de mudança "limpa" (conforme política central de artefatos) usando análise de proveniência de caminho, separando desenvolvimento adiado de retrabalho destrutivo.

#### Entrada (Input)
- Git parent mirrors (data/raw/repos_parent_cache/)
- Policy `code-churn-metrics-v2` e `cc-v2-clean-paths` (validação em 1.2)
- T3 anchor points (data/processed/evaluations/)

#### Escopo
1. Criar `paper_v9/scripts/metrics/m4_clean_change_dynamics.py`
2. M4a: magnitude de churn source/test limpo (LOC)
3. M4b: intensidade por commit tocante e amplitude de caminhos limpos
4. M4c: composição de artefatos e filas de review de desconhecidos
5. M4d: janela diária retrospectiva de 7 dias, alinhada a T3, para churn limpo e caminhos únicos
6. **Não usar contagem de commits como resultado principal**; pertence a M3
7. Usar atomic writes + resume por hash

#### Saída (Output)
- `paper_v9/data/metrics/m4_churn_magnitude.csv`
- `paper_v9/data/metrics/m4_commit_intensity.csv`
- `paper_v9/data/metrics/m4_artifact_composition.csv`
- `paper_v9/data/metrics/m4_rolling_7day_trajectory.csv`
- `paper_v9/data/metrics/m4_churn_magnitude_pooled.csv`
- `paper_v9/data/metrics/m4_commit_intensity_pooled.csv`
- `paper_v9/data/metrics/m4_artifact_composition_pooled.csv`
- `paper_v9/data/metrics/m4_rolling_7day_trajectory_pooled.csv`
- `paper_v9/data/metrics/m4_clean_change_dynamics.metadata.json`
- `paper_v9/scripts/metrics/m4_clean_change_dynamics.py`
- `paper_v9/tests/test_m4.py`
- `paper_v9/verification_notebooks/verify_m4.ipynb`
- `paper_v9/data/metrics/m4_churn_magnitude.csv`
- `paper_v9/data/metrics/m4_commit_intensity.csv`
- `paper_v9/data/metrics/m4_artifact_composition.csv`
- `paper_v9/data/metrics/m4_rolling_7day_trajectory.csv`
- `paper_v9/data/metrics/m4_clean_change_dynamics.metadata.json`
- `paper_v9/scripts/metrics/m4_clean_change_dynamics.py` (testado)

#### Validação
- [ ] M4 usa política de artefatos v2; rejeita v1
- [ ] Churn medido em LOC (não contagem de commits)
- [ ] Janelas de 7 dias alinhadas a T3 ± dias
- [ ] Todas as 14 equipe-semestrais cobertas
- [ ] Atomic writes: `.partial` → rename
- [ ] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** ✓ APROVADO para Tarefa 3.3

---

### Tarefa 3.3 - Implementar e Validar M5 (Evidência Textual de Fricção)

**Dependências:** 1.2 ✓  
**Estimativa:** 3–4 horas  
**Métrica RQ:** RQ2  
**Nota:** Neste moment apenas processamento de corpus, sem LLM novo. LLM futuro será extensão opcional.

#### Objetivo
Reconstruir corpus global por marco a partir de chunks técnicos, medir densidade de marcadores de fricção, sem LLM novo por enquanto.

#### Entrada (Input)
- Transcripts (data/processed/transcripts/) por sessão e semestre
- Segmentação técnica (chunks) de v8 ou documento de análise v8

#### Escopo
1. Criar `paper_v9/scripts/metrics/m5_coordination_evidence.py`
2. M5a: densidade de marcadores por mil tokens (fricção, bloqueio, retrabalho, etc.)
3. M5b: composição por alinhamento/repasse/integração/bloqueio/retrabalho
4. M5c: cobertura de corpus, sessões de origem, chunks técnicos
5. Versionar léxico de marcadores
6. Expor fila auditável de trechos para revisão humana
7. **Proibir correlação com medidas equipe-semestral quando grãos forem incompatíveis** (corpus global ≠ equipe-semestre)

#### Saída (Output)
- `paper_v9/data/metrics/m5_marker_density.csv`
- `paper_v9/data/metrics/m5_marker_composition.csv`
- `paper_v9/data/metrics/m5_corpus_coverage.csv`
- `paper_v9/data/metrics/m5_evidence_audit_trail.csv` (trechos exemplo para revisão)
- `paper_v9/data/metrics/m5_lexicon.json` (versão do léxico)
- `paper_v9/data/metrics/m5_coordination_evidence.metadata.json`
- `paper_v9/scripts/metrics/m5_coordination_evidence.py`
- `paper_v9/tests/test_m5.py`
- `paper_v9/verification_notebooks/verify_m5.ipynb`
- `paper_v9/metricas_v8-analysis/analyze_m5.md`
- `paper_v9/figures/m5_marker_density.{pdf,svg,png}`
- `paper_v9/figures/m5_marker_composition.{pdf,svg,png}`
- `paper_v9/data/metrics/m5_marker_density.html`
- `paper_v9/data/metrics/m5_marker_composition.html`

#### Validação
- [x] Léxico versionado e documentado
- [x] Fila auditável de trechos acessível
- [x] Nenhuma correlação implícita com M3/M4
- [x] Cobertura de corpus clara (qual % de sessões, qual % de tokens)
- [x] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** APROVAÇÃO MANUAL PENDENTE antes da Fase 4 (M6–M9)

---

## Fase 4: RQ3 - Planejamento, Retrabalho e Associações

Objetivo: Implementar métricas que testam se qualidade de artefatos de planejamento no início (T1) associa-se com retrabalho destrutivo tardio e desfechos independentes do projeto.

### Tarefa 4.1 - Implementar e Validar M6a (Planejamento Estrutural)

**Dependências:** 1.2 ✓  
**Estimativa:** 2–3 horas  
**Métrica RQ:** RQ3  

#### Objetivo
Quantificar presença, contagem e escopo de artefatos de planejamento T1 por regra determinística.

#### Entrada (Input)
- T1 artifacts (data/lake/ ou data/processed/) — commits, docs, designs
- Regra de decisão de v8 (paper_v8/METRICS_PLAN.md)

#### Escopo
1. Criar `paper_v9/scripts/metrics/m6_structural_planning.py`
2. M6a: detectar presença/contagem/escopo de artefatos T1 (determinístico, sem LLM)
3. Usar regra de v8 como baseline
4. Criar manifesto com cobertura

#### Saída (Output)
- `paper_v9/data/metrics/m6a_structural_planning.csv`
- `paper_v9/data/metrics/m6_structural_planning.metadata.json`
- `paper_v9/scripts/metrics/m6_structural_planning.py`
- `paper_v9/tests/test_m6.py`
- `paper_v9/verification_notebooks/verify_m6.ipynb`
- `paper_v9/metricas_v8-analysis/analyze_m6.md`
- `paper_v9/figures/m6a_planning_scope_t1.{pdf,svg,png}`
- `paper_v9/figures/m6a_planning_presence_t1.{pdf,svg,png}`
- `paper_v9/data/metrics/m6a_planning_scope_t1.html`
- `paper_v9/data/metrics/m6a_planning_presence_t1.html`

#### Validação
- [x] M6a CSV bem-formado (team_semester, has_planning, artifact_count, scope_score, etc.)
- [x] Todas as 14 equipe-semestrais com scores estruturais
- [x] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** APROVAÇÃO MANUAL PENDENTE para Tarefa 4.2

---

### Tarefa 4.2 - Apresentar Protocolo, Prompt, Custo e Amostra de M6b (Análise LLM de Planejamento)

**Dependências:** 4.1 ✓  
**Estimativa:** 2–3 horas  
**Métrica RQ:** RQ3  

#### Objetivo
**Não executar M6b neste momento.** Apenas apresentar e ganhar aprovação explícita para:
- Protocolo de extração LLM estruturada
- Prompt exato e validação de JSON
- Estimativa de custo (tokens, $)
- Amostra piloto de 2–3 team-semesters com exemplos

#### Entrada (Input)
- T1 planning artifacts (amostra)
- Modelo LLM (p. ex., GPT-4, Llama 2, etc.)
- Budget constraints (se houver)

#### Escopo
1. Criar documento `paper_v9/M6B_LLM_PROTOCOL.md` com:
   - Objetivo de M6b (extrair goals, architecture, task decomposition, risk/dependency)
   - Prompt exato (incluindo contexto, exemplos, instruções de validação)
   - Schema JSON esperado (fields obrigatórios, types, validações)
   - Tratamento de `insufficient_evidence`
2. Rodar piloto em 2–3 team-semesters (amostra estratificada)
3. Gerar `paper_v9/M6B_PILOT_RESULTS.json` com payloads, respostas, tokens consumidos
4. Estimar custo total para 14 team-semesters
5. Documentar cache strategy (se aplicável)

#### Saída (Output)
- `paper_v9/M6B_LLM_PROTOCOL.md` (~2–3 KB, detalhado)
- `paper_v9/M6B_PILOT_RESULTS.json` (exemplos de 2–3 team-semesters)
- `paper_v9/M6B_COST_ESTIMATE.txt` (tokens, custo estimado, duração)
- `paper_v9/data/metrics/m6b_llm_planning_content.json`
- `paper_v9/data/metrics/m6_llm_planning_content.metadata.json`
- `paper_v9/data/metrics/m6b_llm_planning_sample_for_review.md`
- `paper_v9/scripts/metrics/m6_llm_planning_content.py`
- `paper_v9/tests/test_m6b.py`
- Recomendação: "Aprovado para execução?" Sim/Não

#### Validação (Manual)
- [x] Prompt é claro e não ambíguo
- [x] JSON schema e validações estão definidos
- [x] Amostra piloto gera respostas estruturadas — 9 respostas válidas e 5 casos indisponíveis
- [x] Validação de resposta passa em 100% dos registros aceitos
- [x] Custo estimado aceito — execução registrada no ledger central

#### Gate
**Status ao completar:** ✓ APROVADO para execução controlada da Tarefa 4.3

---

### Tarefa 4.3 - Executar M6b (Análise LLM de Planejamento) — Somente Após Aprovação de 4.2

**Dependências:** 4.2 ✓ (aprovação explícita)  
**Estimativa:** 2–4 horas (incluindo cache, retries)  
**Métrica RQ:** RQ3  

#### Objetivo
Executar extração estruturada LLM em todas as 14 equipe-semestrais, persistindo payloads/respostas/cache. Criar amostra para revisão humana antes de permitir em texto principal.

#### Entrada (Input)
- Protocolo aprovado (M6B_LLM_PROTOCOL.md)
- T1 planning artifacts (todos os 14 team-semesters)
- Budget aprovado

#### Escopo
1. Criar `paper_v9/scripts/metrics/m6_llm_planning_content.py`
2. Executar prompt LLM em todos os 14 team-semesters
3. Persistir: payload (input), resposta bruta (output), cache key, modelo/temperatura/versão
4. Validar JSON resposta conforme schema
5. Tratar `insufficient_evidence` explicitamente
6. Gerar `paper_v9/data/metrics/m6b_llm_planning_content.json` (todos os resultados)
7. Estratificar amostra para revisão humana (top 3, bottom 3, middle 2)

#### Saída (Output)
- `paper_v9/data/metrics/m6b_llm_planning_content.json` (todas as 14 respostas + metadados)
- `paper_v9/data/metrics/m6b_llm_planning_sample_for_review.md` (amostra de 8 team-semesters com notas)
- `paper_v9/data/metrics/m6_llm_planning_content.metadata.json` (cache keys, custos realizados, versão modelo)
- `paper_v9/scripts/metrics/m6_llm_planning_content.py` (testado, com cache)

#### Validação (técnica)
- [x] Todas as 14 respostas são JSON válido
- [x] Todos os fields obrigatórios presentes
- [x] `insufficient_evidence` declarado onde apropriado
- [x] Payloads versionados (permitir reproducibilidade)
- [x] Cache funcionando (rerun não gasta tokens)
- [x] Amostra revisada e aprovada; oito casos documentados

#### Gate
**Status ao completar:** ✓ APROVADO para uso exploratório estruturado; sem score composto

---

### Tarefa 4.4 - Implementar e Validar M7 (Dinâmica de Inatividade de Repositório)

**Dependências:** 1.2 ✓  
**Estimativa:** 2–3 horas  
**Métrica RQ:** RQ3  

#### Objetivo
Capturar trajetória de inatividade de repositório, usando janelas retrospectivas de 7 dias ancoradas em T3.

#### Entrada (Input)
- Git parent mirrors (data/raw/repos_parent_cache/)
- T3 anchor points (data/processed/evaluations/)

#### Escopo
1. Criar `paper_v9/scripts/metrics/m7_repository_inactivity.py`
2. M7a: trajetória diária de inatividade em janelas de 7 dias, -63 a +7 dias de T3
3. M7b: padrão por checkpoints (nunca inativa, apenas T1, intermitente)
4. M7c: cobertura de avaliação T1 entre equipes inativas
5. Rótulo exato: `repository_inactivity` (não `planning_omission`)

#### Saída (Output)
- `paper_v9/data/metrics/m7_inactivity_trajectory.csv`
- `paper_v9/data/metrics/m7_inactivity_pattern.csv`
- `paper_v9/data/metrics/m7_repository_inactivity.metadata.json`
- `paper_v9/scripts/metrics/m7_repository_inactivity.py`
- `paper_v9/tests/test_m7.py`
- `paper_v9/verification_notebooks/verify_m7.ipynb`
- `paper_v9/metricas_v8-analysis/analyze_m7.md`
- `paper_v9/data/metrics/m7_checkpoint_inactivity.csv`
- `paper_v9/data/metrics/m7_inactivity_trajectory.html`
- `paper_v9/figures/m7_repository_inactivity_trajectory.{pdf,svg,png}`

#### Validação
- [x] Trajetórias de 71 janelas (−63 a +7) cobertas
- [x] Rótulo `repository_inactivity` usado
- [x] Padrões por checkpoint claros
- [x] Cobertura T1 documentada
- [x] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** APROVAÇÃO MANUAL PENDENTE antes da Tarefa 4.5

---

### Tarefa 4.5 - Implementar e Validar M8 (Retrabalho Limpo com Baseline)

**Dependências:** 1.2 ✓ (validação code-churn-metrics-v2), 3.2 ✓ (M4 fornece política)  
**Estimativa:** 4–5 horas  
**Métrica RQ:** RQ3  

#### Objetivo
Medir magnitude de retrabalho limpo em caminhos com baseline T1/T2, condicionado à proveniência de caminho e elegibilidade de baseline.

#### Entrada (Input)
- Git parent mirrors (data/raw/repos_parent_cache/)
- Política `code-churn-metrics-v2` (M4)
- T1/T2 baseline (git snapshots em checkpoints)
- T3 anchor points

#### Escopo
1. Criar `paper_v9/scripts/metrics/m8_clean_rework.py`
2. M8a: magnitude de retrabalho limpo em caminhos com baseline T1/T2 (LOC)
3. M8b: participação de retrabalho limpo no churn T3 (razão, somente if baseline + churn > 0)
4. M8c: trajetória diária de retrabalho limpo em janelas de 7 dias, -21 a +7 dias de T3
5. M8d: número de caminhos limpos pré-existentes e elegibilidade de baseline
6. **Sempre reportar:** zeros, cobertura, mediana, total, máximo, participação do máximo
7. Não chamar proveniência de caminho de "defeito" sem validação semântica
8. Usar mesma política de M4

#### Saída (Output)
- `paper_v9/data/metrics/m8_rework_magnitude.csv`
- `paper_v9/data/metrics/m8_rework_participation.csv`
- `paper_v9/data/metrics/m8_rework_trajectory.csv`
- `paper_v9/data/metrics/m8_baseline_eligibility.csv`
- `paper_v9/data/metrics/m8_clean_rework.metadata.json`
- `paper_v9/scripts/metrics/m8_clean_rework.py`
- `paper_v9/tests/test_m8.py`
- `paper_v9/verification_notebooks/verify_m8.ipynb`
- `paper_v9/metricas_v8-analysis/analyze_m8.md`
- `paper_v9/data/metrics/m8_clean_rework_trajectory.html`
- `paper_v9/figures/m8_clean_rework_trajectory.{pdf,svg,png}`

#### Validação
- [x] M8 usa mesma política de artefatos de M4
- [x] Zeros, mediana, máximo reportados explicitamente
- [x] Razão M8b somente para baseline elegível + churn > 0
- [x] Trajetórias de 29 janelas inclusivas (−21 a +7) cobertas
- [x] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** APROVAÇÃO MANUAL PENDENTE antes da Tarefa 4.6

---

### Tarefa 4.6 - Implementar e Validar M9 (Associações Estratificadas)

**Dependências:** 4.1 ✓ (M6a), 4.3+ (M6b somente se aprovado), 4.5 ✓ (M8), independentes de outcomes T3  
**Estimativa:** 3–4 horas  
**Métrica RQ:** RQ3  

#### Objetivo
Calcular associações descritivas entre planning (M6a/M6b) e rework/outcomes (M8a/M8b), com estratificação, cobertura clara, e intervalos leave-one-out.

#### Entrada (Input)
- M6a (Tarefa 4.1)
- M6b se aprovado (Tarefa 4.3); se não, só M6a
- M8a, M8b (Tarefa 4.5)
- Outcomes T3 independentes (avaliador blind-scored)

#### Escopo
1. Criar `paper_v9/scripts/metrics/m9_structured_associations.py`
2. M9a: M6a vs. M8a em todas as 14 equipe-semestrais (Spearman descritivo)
3. M9b: M6a vs. M8b somente no estrato elegível para razão retrabalho
4. M9c: M6a vs. outcomes independentes T3 dos avaliadores
5. M9d: M6b vs. outcomes somente após aprovação humana de M6b (condicional)
6. Produzir Spearman descritivo (ρ, p-value), tabela cobertura/estratos, intervalo leave-one-out
7. **Não imputar nota 1 para ausência de Git**
8. **Não usar M7 como preditor independente**
9. Declarar denominador, estrato, ausências, influência de casos extremos

#### Saída (Output)
- `paper_v9/data/metrics/m9_planning_vs_rework_m6a_m8a.csv` (todos os 14 team-semesters, Spearman)
- `paper_v9/data/metrics/m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv` (subset elegível)
- `paper_v9/data/metrics/m9_planning_vs_outcomes_m6a_t3.csv` (outcomes blind-scored)
- `paper_v9/data/metrics/m9_planning_vs_outcomes_m6b_t3_if_approved.csv` (condicional a 4.3)
- `paper_v9/data/metrics/m9_leave_one_out_intervals.csv` (jacknife para sensibilidade)
- `paper_v9/data/metrics/m9_structured_associations.metadata.json`
- `paper_v9/scripts/metrics/m9_structured_associations.py`
- `paper_v9/tests/test_m9.py`
- `paper_v9/verification_notebooks/verify_m9.ipynb`
- `paper_v9/metricas_v8-analysis/analyze_m9.md`
- `paper_v9/data/metrics/m9_structured_associations.html`
- `paper_v9/figures/m9_structured_associations.{pdf,svg,png}`

#### Validação
- [x] Todos os numeradores/denominadores declarados
- [x] Estratificação clara (qual subset, por quê)
- [x] Leave-one-out intervalos razoáveis (não invertidos)
- [x] M7 não aparece como preditor
- [x] Ausências e casos extremos documentados
- [x] Segunda execução reutiliza (checksum match)

#### Gate
**Status ao completar:** APROVAÇÃO MANUAL PENDENTE antes da Fase 5 (Resultados e Visualizações)

---

## Fase 5: Resultados e Visualizações

Objetivo: Consolidar artefatos M1–M9 em catálogo de resultados rastreável, gerar candidatos de visualização, e aprovar tabelas/figuras finais antes de LaTeX.

### Tarefa 5.1 - Gerar Catálogo de Artefatos de Resultados

**Dependências:** Todas as tarefas de métricas (2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 4.5, 4.6) ✓; 4.3 se aprovado  
**Estimativa:** 2–3 horas  
**Prioridade:** ALTA

#### Objetivo
Consolidar M1–M9 em JSON único `results_summary.json` com números aprovados para LaTeX. Falhar se referências apontarem para artefatos/metadados ausentes.

#### Entrada (Input)
- Todos os CSVs e metadados de M1–M9 (paper_v9/data/metrics/)
- Manifesto de entrada (Tarefa 1.2)

#### Escopo
1. Criar `paper_v9/scripts/results/build_results_summary.py`
2. Consolidar números-chave de M1–M9 em único JSON
3. Validar referências (todos os CSVs existem, checksums conferem)
4. Falhar graciosamente com mensagens claras se dados faltam
5. Gerar `paper_v9/data/results/results_summary.json`

#### Saída (Output)
- `paper_v9/data/results/results_summary.json` (~5–10 KB, validado)
- `paper_v9/scripts/results/build_results_summary.py` (testado)
- Relatório de validação (`paper_v9/RESULTS_VALIDATION.txt`)

#### Validação
- [ ] JSON bem-formado e completo
- [ ] Todas as referências resolvidas
- [ ] Segunda execução produce JSON idêntico

#### Gate
**Status ao completar:** ✓ APROVADO para Tarefa 5.2

---

### Tarefa 5.2 - Gerar Candidatos de Visualização e Realizar Oficina de Escolha

**Dependências:** 5.1 ✓  
**Estimativa:** 3–4 horas (depende de iteração com usuário)  
**Prioridade:** ALTA

#### Objetivo
Gerar 4–5 candidatos de visualização (tabelas + figuras), com dados subjacentes e trade-offs, para aprovação humana antes de entrar em LaTeX.

#### Entrada (Input)
- `results_summary.json` (Tarefa 5.1)
- Dados M1–M9 completos

#### Escopo
1. Criar `paper_v9/scripts/results/generate_figure_candidates.py`
2. Candidato RQ1: painel pequeno M1 (indicadores separados) + ranking M2
3. Candidato RQ2: painel temporal M3/M4d/M5 (eixos explícitos, sem correlação implícita)
4. Candidato RQ3: perfil equipe-semestral (M6a/M8a/M8b/elegibilidade + M8c trajetória)
5. Candidato RQ3: intervalos leave-one-out M9 (qual formato: gráfico forest-plot ou tabela?)
6. Gerar CSVs de dados subjacentes (um per figura)
7. Documentar trade-offs: clareza vs. densidade, evidência vs. impacto visual

#### Saída (Output)
- `paper_v9/figures/candidates_rq1_perception_panel.pdf` + `_data.csv`
- `paper_v9/figures/candidates_rq2_temporal_dynamics.pdf` + `_data.csv`
- `paper_v9/figures/candidates_rq3_planning_rework_profile.pdf` + `_data.csv`
- `paper_v9/figures/candidates_rq3_associations_leave_one_out.pdf` + `_data.csv`
- `paper_v9/FIGURES_CANDIDATES_WORKSHOP.md` (3–5 KB, descrição de cada candidato + trade-offs)
- `paper_v9/scripts/results/generate_figure_candidates.py` (testado)

#### Validação (Manual)
- [ ] Cada candidato tem CSV de dados
- [ ] Cada candidato documenta seu propósito e limitações
- [ ] Trade-offs são claros e justificados
- [ ] Nenhuma figura entra em LaTeX antes de aprovação explícita

#### Gate
**Status ao completar:** Aguardar aprovação manual de figuras antes de Tarefa 6.1

---

## Fase 6: Preparação LaTeX

Objetivo: Criar esqueleto LaTeX modular que aceita figuras aprovadas e numeração rastreável.

### Tarefa 6.1 - Criar Esqueleto LaTeX Modular Compilável

**Dependências:** 0.1 ✓ (ambiente LaTeX), 5.2 ✓ (figuras aprovadas)  
**Estimativa:** 2–3 horas  
**Prioridade:** ALTA

#### Objetivo
Estabelecer estrutura LaTeX modular onde cada seção é arquivo separado, figuras estão em `paper_v9/figures/`, e numeração é rastreável via manifesto.

#### Entrada (Input)
- `paper_v8/latex_code/main.tex` (baseline v8, read-only)
- Figuras aprovadas de 5.2
- REPRODUCIBILITY.md (ambiente LaTeX validado)

#### Escopo
1. Criar `paper_v9/latex/main.tex` (preâmbulo, título, autores, `\input` de seções)
2. Criar 8 arquivos de seção em `paper_v9/latex/sections/`:
   - abstract.tex
   - introduction.tex
   - background_related_work.tex
   - methodology.tex
   - results.tex
   - discussion.tex
   - threats_to_validity.tex
   - conclusion.tex
3. Copiar `references.bib` de v8 (ler-only até revisão)
4. Criar `paper_v9/latex/tables/` para tabelas (se houver)
5. Linkar figuras: `../figures/` (caminhos relativos)
6. Adicionar comentários invisíveis de proveniência: `% M1 data: paper_v9/data/metrics/m1_*.csv`
7. Compilar e verificar estrutura (sem conteúdo ainda)

#### Saída (Output)
- `paper_v9/latex/main.tex` (~50 linhas, structure only)
- `paper_v9/latex/sections/abstract.tex` (placeholder)
- `paper_v9/latex/sections/introduction.tex` (placeholder)
- `paper_v9/latex/sections/background_related_work.tex` (placeholder)
- `paper_v9/latex/sections/methodology.tex` (placeholder)
- `paper_v9/latex/sections/results.tex` (placeholder)
- `paper_v9/latex/sections/discussion.tex` (placeholder)
- `paper_v9/latex/sections/threats_to_validity.tex` (placeholder)
- `paper_v9/latex/sections/conclusion.tex` (placeholder)
- `paper_v9/latex/references.bib` (copied from v8)
- `paper_v9/latex/build/main.pdf` (esqueleto compilável, sem conteúdo)

#### Validação
- [ ] `pdflatex main.tex` compila sem erros (placeholders OK)
- [ ] PDF gera com estrutura (TOC, section numbers)
- [ ] Caminhos de figuras relativos (não absolutos)
- [ ] Comentários de proveniência invisíveis no PDF

#### Gate
**Status ao completar:** ✓ APROVADO para Fase 7 (Revisão Editorial)

---

## Fase 7: Revisão Editorial (Ordem Obrigatória)

Objetivo: Reescrever cada seção em ordem fixada (Methodology → Results → Discussion → Threats → Conclusion → Abstract → Introduction → Background), com aprovação manual entre cada uma.

**Orientação Geral para Fase 7:**
- Uma seção só avança quando a seção anterior for aprovada
- Toda afirmação quantitativa deve ter referência em `results_summary.json`
- Remover afirmações v8 que não sejam sustentadas por dados v9
- Idioma: English técnico internacional; nenhum jargão de pipeline

---

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
- Distinguir uso real de IA `available_but_not_included_in_m1_v1` quando houver
   campos brutos de frequência, tarefas, ferramentas ou experiência, de
   `unavailable_not_measured` quando faltarem unidade temporal, linkage ou
   cobertura válida para a análise pretendida.

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