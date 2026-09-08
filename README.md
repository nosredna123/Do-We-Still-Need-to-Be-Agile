# Do-We-Still-Need-to-Be-Agile

Pipeline inicial para gerar, anonimizar, enriquecer e analisar os dados do artigo **"Do We Still Need to Be Agile?"**.

## Scripts implementados

- `run_pipeline.py`: orquestra as etapas da Fase 1 na ordem definida.
- `00_audio_preparer.py`: comprime e segmenta áudios para o limite da API.
- `00_audio_transcriber.py`: transcreve áudios preparados em português para `.txt` e `.json`.
- `01_ner_extractor.py`: usa OpenAI para identificar candidatos a nomes de pessoas em transcrições brutas.
- `01_anonymizer.py`: anonimiza CSVs e transcrições, gerando `chave_relacional.json`.
- `02_git_parser.py`: extrai histórico Git anonimizado e espelha repositórios sem `.git`.
- `03_data_lake_builder.py`: gera seis Parquets independentes por granularidade e um relatório de validação.
- `04_nlp_qualitative_miner.py`, `05_metric_engine.py`, `06_statistical_analyzer.py` e `07_dashboard_app.py`: scripts futuros da Fase 2, ainda não implementados.

## Dependências mínimas

```bash
pip install -r requirements.txt
```

Dependências opcionais por script:

- `openai` para `00_audio_transcriber.py --backend openai` e `04_nlp_qualitative_miner.py --backend openai`
- `openai-whisper` para `00_audio_transcriber.py --backend whisper`
- `streamlit` para `07_dashboard_app.py`
- `ffmpeg` para `00_audio_preparer.py`; no Ubuntu/Debian, instale com `sudo apt install ffmpeg`.

## Configuração

Defina segredos e configurações compartilhadas no arquivo `.env` na raiz do
projeto. Todos os scripts da Fase 1 carregam esse arquivo no início da execução,
sem sobrescrever variáveis já definidas no ambiente.

```dotenv
OPENAI_API_KEY=sua_chave
ANONYMIZATION_SALT=segredo_aleatorio
```

O módulo `pipeline_core.py` centraliza funções reutilizáveis do pipeline,
incluindo a carga da configuração compartilhada. Ele não inicia nem orquestra
as etapas. `run_pipeline.py` é o ponto de entrada para a execução coordenada;
os scripts numerados continuam disponíveis como pontos de entrada independentes.

Os modelos e parâmetros de requisição ficam centralizados em
`pipeline_config.py`, em `MODEL_CONFIG`. A configuração atual mantém
`whisper-1` para transcrição e `gpt-4o-mini` para NER. O catálogo também reserva
a configuração da futura mineração qualitativa, sem armazenar credenciais ou
dados de origem.

Todos os prompts enviados a serviços externos de IA ficam centralizados em
`pipeline_prompts.py`. Esse catálogo é a referência auditável para pesquisadores
e não pode conter PII, segredos, nomes reais ou outros dados de origem.

Decisões metodológicas não sigilosas, como os cortes temporais de formulários,
ficam centralizadas e versionadas em `pipeline_config.py`. Esse módulo não pode
conter PII, credenciais nem valores de dados brutos.

Sob supervisão do pesquisador, os áudios brutos são enviados à OpenAI para
transcrição e as transcrições brutas são enviadas uma vez à OpenAI para NER. A
prioridade de proteção deste projeto é impedir que PII seja exposta nos artefatos
processados, no Data Lake, no pacote de replicação ou em material publicado. A
etapa NER armazena somente candidatos a pessoas, nunca o texto transcrito, e seus
artefatos são privados e ignorados pelo Git. Todo `data/processed/` e `data/lake/`
é privado por padrão; um pacote de replicação deve exportar somente artefatos
auditados após a verificação de PII. O `ANONYMIZATION_SALT` nunca é enviado à OpenAI.

## Execução da Fase 1

O orquestrador executa as etapas na ordem `prepare`, `transcribe`, `ner`,
`anonymize`, `git` e `lake`, usando o mesmo interpretador Python que o iniciou. A preparação
converte os áudios originais para MP3 mono a 16 kHz e 48 kbps em
`data/processed/audio_chunks`; arquivos que ainda ultrapassem 25 MiB são
divididos em segmentos de 10 minutos. A transcrição consome somente esses
arquivos preparados e envia `language="pt"` e um prompt genérico para preservar
nomes próprios, siglas, termos técnicos e pontuação. O prompt não contém PII e
não substitui a anonimização local posterior. O NER usa `gpt-4o-mini` e resposta
JSON estrita para identificar candidatos a pessoas, processando apenas
transcrições pendentes por checksum. A anonimização busca
recursivamente CSVs em `data/raw/forms` e transcrições `.txt` e `.json` em
`data/processed/transcripts`; os resultados são escritos em
`data/processed/forms` e `data/processed/transcripts_anon`, preservando os
caminhos relativos. `ANONYMIZATION_SALT` é obrigatório, salvo quando `--salt` é
fornecido explicitamente.

```bash
.venv/bin/python run_pipeline.py \
	--dry-run
```

Para executar a pipeline em lotes, use `--limite` com a quantidade máxima de
itens pendentes por estágio incremental:

```bash
.venv/bin/python run_pipeline.py --stages prepare transcribe --limite 10
.venv/bin/python run_pipeline.py --stages ner anonymize --limite 10
```

O limite considera somente entradas sem artefato atual; ao repetir o comando,
o próximo lote é selecionado automaticamente. A opção se aplica a
`prepare`, `transcribe`, `ner` e `anonymize`. As etapas `git` e `lake` não
aceitam lotes parciais porque produzem artefatos agregados.

Use `--csv` e `--transcript` para acrescentar arquivos fora dos diretórios
padrão. Artefatos com metadados válidos e checksum inalterado são ignorados;
novos ou alterados são processados individualmente. Use `--stages` para executar
etapas específicas, `--from-stage` e `--to-stage` para uma faixa contínua,
`--dry-run` para apenas listar os comandos, e `--force` para propagar a
regeneração intencional a todas as etapas selecionadas.

Os formulários de avaliadores devem ser salvos como um CSV por semestre em
`data/raw/forms/<semestre>/avaliadores.csv`. O marcador temporal é derivado do
`Timestamp` por `temporal_marker_for()` em `pipeline_config.py`. As datas são
definidas em ISO-8601 e, em `2025.2`, os pares 17/10-24/10, 14/11-21/11 e
05/12-12/12 representam respectivamente T1, T2 e T3. Cada par é um único corte
distribuído em dois dias por capacidade de apresentação. Em `2026.1`, 24/04,
22/05 e 19/06 correspondem a T1, T2 e T3.

Para commits Git, a classificação temporal usa fases contínuas e não as janelas
estreitas de apresentação: datas anteriores ao início de T1 recebem `T1`, datas
a partir de T1 e anteriores a T2 recebem `T2`, e datas a partir de T2 recebem
`T3`. Essa regra é separada da regra estrita usada nos formulários de avaliadores.

```bash
.venv/bin/python run_pipeline.py --stages git lake --dry-run
.venv/bin/python run_pipeline.py --from-stage anonymize --to-stage lake --force
```

O estágio `lake` gera `data/lake/student_responses.parquet`,
`data/lake/evaluator_team_cuts.parquet`, `data/lake/git_team_cuts.parquet`,
`data/lake/git_commits.parquet`, `data/lake/git_files.parquet` e
`data/lake/transcript_sessions.parquet`, cada um com seu sidecar de checksum.
Também gera `data/lake/lake_validation_report.json`. Não existe exportação
`master_dataset.parquet`. `git_match_status` em `evaluator_team_cuts` vale
`matched` quando há atividade Git para a mesma equipe, semestre e corte, e
`no_observed_activity` quando essa atividade não foi observada.
As perguntas de score são convertidas para nomes analíticos estáveis, como
`engagement_participation_mean`, `project_progress_mean`,
`scope_applicability_mean` e `technical_complexity_mean`. Cada score também
possui `_std` (desvio padrão amostral), `_median`, `_iqr` e `_n` (quantidade de
respostas válidas) para cada equipe, semestre e corte.

### Métricas estatísticas do Data Lake

As estatísticas dos avaliadores são calculadas dentro de cada chave
`ID_Equipe + Semestre + temporal_marker`. Elas descrevem a distribuição das
respostas dos avaliadores para aquele corte, e não uma média global entre
equipes ou semestres.

Para cada score, são produzidas as seguintes métricas:

- **`_mean` (média):** soma das respostas válidas dividida pela quantidade de
	respostas válidas. É o valor central atualmente preservado na coluna
	analítica principal.
- **`_std` (desvio padrão amostral):** mede quanto as respostas variam em torno
	da média. É calculado com `ddof=1`, apropriado quando as respostas observadas
	são tratadas como uma amostra de avaliadores. Com apenas uma resposta, o
	valor é `NaN`, pois não há informação suficiente para estimar a variabilidade.
- **`_median` (mediana):** valor que divide as respostas ordenadas ao meio.
	É menos sensível que a média a uma resposta muito alta ou muito baixa.
- **`_iqr` (intervalo interquartil):** mede a dispersão dos 50% centrais das
	respostas. É calculado como `Q3 - Q1`, em que `Q1` é o percentil 25 e `Q3` é
	o percentil 75. Por exemplo, se `Q1 = 1` e `Q3 = 2`, então `IQR = 1`.
	Quanto maior o IQR, maior a dispersão central entre os avaliadores.
- **`_n` (quantidade válida):** número de respostas não nulas usadas para
	calcular aquele score. O valor pode variar entre scores se houver respostas
	ausentes em perguntas específicas.

As métricas de score mantêm os valores originais das perguntas em uma escala
analítica estável, mas não preservam a identidade dos avaliadores. Portanto,
`_n` representa respostas válidas observadas, não necessariamente avaliadores
distintos, caso a fonte contenha submissões duplicadas.

No dataset `git_team_cuts`, os principais agregados são `lines_added`,
`lines_deleted` e `files_changed` somados por equipe, semestre e corte;
`num_authors` conta autores locais distintos e `num_commits` conta commits.
O campo `git_match_status` em `evaluator_team_cuts` informa se existe uma chave
Git correspondente, sem copiar essas métricas para as linhas de avaliação.

Para validar a implementação, execute `.venv/bin/pytest -x`. Os dados em
`data/processed/` e `data/lake/` permanecem privados e ignorados pelo Git.

## Exemplo de uso

```bash
python 01_anonymizer.py --csv dados/alunos.csv --transcript dados/feedback.txt --output-dir outputs/anon --mapping-path outputs/chave_relacional.json
python 02_git_parser.py --repos-list dados/repos_list.csv --output-csv outputs/git_logs_anon.csv --output-commits outputs/git_commits_anon.csv --output-files outputs/git_files_anon.csv --cache-dir outputs/repos
python 03_data_lake_builder.py --forms-dir outputs/anon --git-commits outputs/git_commits_anon.csv --git-files outputs/git_files_anon.csv --transcripts-dir outputs/transcripts_anon --output-dir outputs/lake
# A Fase 2 ainda será implementada sobre os seis contratos do lake.
```

## Convenções adotadas

- As etapas da Fase 1 são fail-fast: falhas de API, fontes ausentes ou
	inválidas, repositórios inacessíveis e dados malformados encerram a etapa e
	impedem a geração de resultados parciais. A transcrição OpenAI aceita no
	máximo 25 MiB por arquivo; divida ou comprima gravações maiores antes de rodar.
- Os áudios preparados em `data/processed/audio_chunks` são dados derivados e
	permanecem fora do Git, assim como os áudios brutos.
- A anonimização usa hashes SHA-256 truncados com prefixo `anon_`.
- A anonimização de transcrições substitui e-mails, rótulos de falantes e os
	nomes de pessoas identificados pelo NER. Candidatos NER e mapeamentos são
	artefatos privados e não devem ser publicados.
- Os datasets tabulares centrais são persistidos em Parquet.
- As visualizações são exportadas em SVG para facilitar versionamento e publicação.
- Os produtores da Fase 1 registram um checksum SHA-256 em sidecars `.metadata.json` e ignoram somente artefatos com status `success` e entradas inalteradas. Use `--force` para regenerar um artefato intencionalmente.
