# Do-We-Still-Need-to-Be-Agile

Pipeline inicial para gerar, anonimizar, enriquecer e analisar os dados do artigo **"Do We Still Need to Be Agile?"**.

## Scripts implementados

- `run_pipeline.py`: orquestra as etapas da Fase 1 na ordem definida.
- `00_audio_preparer.py`: comprime e segmenta áudios para o limite da API.
- `00_audio_transcriber.py`: transcreve áudios preparados em português para `.txt` e `.json`.
- `01_anonymizer.py`: anonimiza CSVs e transcrições, gerando `chave_relacional.json`.
- `02_git_parser.py`: extrai histórico Git anonimizado e espelha repositórios sem `.git`.
- `03_data_lake_builder.py`: consolida entradas anonimizadas em `master_dataset.parquet`.
- `04_nlp_qualitative_miner.py`: enriquece o dataset com sinais de sentimento, tópicos, estilo de trabalho e exaustão.
- `05_metric_engine.py`: calcula Planejamento Inicial, Code Churn, Degradação Técnica, Atrito de Integração e Índice de Esgotamento.
- `06_statistical_analyzer.py`: gera correlações, teste de hipótese e gráficos SVG em `assets/figures/`.
- `07_dashboard_app.py`: expõe um dashboard Streamlit sobre a relação entre planejamento e code churn.

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

## Execução da Fase 1

O orquestrador executa as etapas na ordem `prepare`, `transcribe`, `anonymize`,
`git` e `lake`, usando o mesmo interpretador Python que o iniciou. A preparação
converte os áudios originais para MP3 mono a 16 kHz e 48 kbps em
`data/processed/audio_chunks`; arquivos que ainda ultrapassem 25 MiB são
divididos em segmentos de 10 minutos. A transcrição consome somente esses
arquivos preparados e envia `language="pt"` para a API. A anonimização busca
recursivamente CSVs em `data/raw/forms` e transcrições `.txt` e `.json` em
`data/processed/transcripts`; os resultados são escritos em
`data/processed/forms` e `data/processed/transcripts_anon`, preservando os
caminhos relativos. `ANONYMIZATION_SALT` é obrigatório, salvo quando `--salt` é
fornecido explicitamente.

```bash
.venv/bin/python run_pipeline.py \
	--dry-run
```

Use `--csv` e `--transcript` para acrescentar arquivos fora dos diretórios
padrão. Artefatos com metadados válidos e checksum inalterado são ignorados;
novos ou alterados são processados individualmente. Use `--stages` para executar
etapas específicas, `--from-stage` e `--to-stage` para uma faixa contínua,
`--dry-run` para apenas listar os comandos, e `--force` para propagar a
regeneração intencional a todas as etapas selecionadas.

```bash
.venv/bin/python run_pipeline.py --stages git lake --dry-run
.venv/bin/python run_pipeline.py --from-stage anonymize --to-stage lake --force
```

## Exemplo de uso

```bash
python 01_anonymizer.py --csv dados/alunos.csv --transcript dados/feedback.txt --output-dir outputs/anon --mapping-path outputs/chave_relacional.json
python 02_git_parser.py --repos-list dados/repos_list.csv --output-csv outputs/git_logs_anon.csv --cache-dir outputs/repos
python 03_data_lake_builder.py --forms-dir outputs/anon --git-logs outputs/git_logs_anon.csv --output-parquet outputs/master_dataset.parquet
python 04_nlp_qualitative_miner.py --input outputs/master_dataset.parquet --output outputs/nlp_enriched_dataset.parquet
python 05_metric_engine.py --input outputs/nlp_enriched_dataset.parquet --output outputs/metrics_dataset.parquet
python 06_statistical_analyzer.py --input outputs/metrics_dataset.parquet --correlation-output outputs/correlation_results.csv --figures-dir assets/figures
streamlit run 07_dashboard_app.py -- --input outputs/metrics_dataset.parquet
```

## Convenções adotadas

- As etapas da Fase 1 são fail-fast: falhas de API, fontes ausentes ou
	inválidas, repositórios inacessíveis e dados malformados encerram a etapa e
	impedem a geração de resultados parciais. A transcrição OpenAI aceita no
	máximo 25 MiB por arquivo; divida ou comprima gravações maiores antes de rodar.
- Os áudios preparados em `data/processed/audio_chunks` são dados derivados e
	permanecem fora do Git, assim como os áudios brutos.
- A anonimização usa hashes SHA-256 truncados com prefixo `anon_`.
- A anonimização de transcrições substitui e-mails, rótulos de falantes e nomes
	próprios identificáveis mencionados no texto corrido.
- Os datasets tabulares centrais são persistidos em Parquet.
- As visualizações são exportadas em SVG para facilitar versionamento e publicação.
- Os produtores da Fase 1 registram um checksum SHA-256 em sidecars `.metadata.json` e ignoram somente artefatos com status `success` e entradas inalteradas. Use `--force` para regenerar um artefato intencionalmente.
