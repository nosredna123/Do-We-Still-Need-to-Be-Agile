# Do-We-Still-Need-to-Be-Agile

Pipeline inicial para gerar, anonimizar, enriquecer e analisar os dados do artigo **"Do We Still Need to Be Agile?"**.

## Scripts implementados

- `00_audio_transcriber.py`: transcreve áudios para `.txt` e `.json` usando `whisper`, `openai` ou `txt-sidecar`.
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

## Configuração

Defina segredos e configurações compartilhadas no arquivo `.env` na raiz do
projeto. Todos os scripts da Fase 1 carregam esse arquivo no início da execução,
sem sobrescrever variáveis já definidas no ambiente.

```dotenv
OPENAI_API_KEY=sua_chave
```

O módulo `pipeline_core.py` centraliza funções reutilizáveis do pipeline,
incluindo a carga da configuração compartilhada. Ele não inicia nem orquestra
as etapas: cada script numerado é um ponto de entrada independente.

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

- A anonimização usa hashes SHA-256 truncados com prefixo `anon_`.
- Os datasets tabulares centrais são persistidos em Parquet.
- As visualizações são exportadas em SVG para facilitar versionamento e publicação.
- Os produtores da Fase 1 registram um checksum SHA-256 em sidecars `.metadata.json` e ignoram somente artefatos com status `success` e entradas inalteradas. Use `--force` para regenerar um artefato intencionalmente.
