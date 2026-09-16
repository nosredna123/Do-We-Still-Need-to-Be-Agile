## POC — Recuperação de Informações em Bulas de Medicamentos com LangChain e ChromaDB

Este projeto é uma Prova de Conceito (POC) que demonstra Recuperação Aumentada por Geração (RAG) sobre um PDF de bulas de medicamentos. O fluxo principal:

- Carrega o PDF `guia-medicamentos.pdf`.
- Segmenta o conteúdo por medicamento usando expressão regular.
- Gera embeddings locais com `SentenceTransformers (all-MiniLM-L6-v2)` via `langchain-huggingface`.
- Indexa e persiste os vetores no `ChromaDB` (diretório `chroma_bulas_db`).
- Compara respostas com RAG (usando recuperador + Gemini) versus sem RAG (somente Gemini).


### Arquivos principais

- `test.py`: script que executa todo o fluxo (carregamento, chunking, indexação, consultas e comparação RAG vs. sem RAG).
- `guia-medicamentos.pdf`: documento de entrada contendo as bulas.
- `chroma_bulas_db/`: diretório de persistência do banco vetorial Chroma.


### Requisitos

- Python 3.10+ (recomendado)
- Windows 10/11 (projeto desenvolvido/testado em PowerShell)
- Chave de API do Google para o Gemini (Google Generative AI)


### Dependências Python

Instale as bibliotecas abaixo (sem fixar versões para simplificar a POC):

```bash
pip install \
  langchain \
  langchain-community \
  langchain-google-genai \
  langchain-huggingface \
  sentence-transformers \
  chromadb \
  pypdf
```

Observações:

- `PyPDFLoader` (usado em `test.py`) depende de `pypdf`.
- O primeiro uso de `sentence-transformers` baixa o modelo `all-MiniLM-L6-v2` automaticamente (pode levar alguns minutos na primeira execução).


### Como configurar (Windows PowerShell)

1) (Opcional) Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instale as dependências (ver seção anterior).

3) Configure a chave do Google para o Gemini. O script `test.py` atualmente usa a variável `GOOGLE_API_KEY` definida dentro do próprio arquivo. Você pode:

- Editar o valor diretamente em `test.py` substituindo `"your_key"` pela sua chave;
  ou
- Exportar a variável de ambiente e adaptar o código para lê-la, se preferir. Exemplo de export no PowerShell:

```bash
$env:GOOGLE_API_KEY = "SUA_CHAVE_AQUI"
```

4) Garanta que o arquivo `guia-medicamentos.pdf` esteja na raiz do projeto (mesmo nível de `test.py`).


### Como executar

```bash
python .\test.py
```

Na primeira execução, o índice vetorial será criado e persistido em `chroma_bulas_db/`. Em seguida, o script fará três consultas de exemplo e imprimirá no console:

- O tempo e a resposta usando RAG (recuperação + LLM);
- O tempo e a resposta usando apenas LLM (sem RAG).


### O que o script faz (visão técnica)

- Carrega e concatena as páginas do PDF com `PyPDFLoader`.
- Separa o conteúdo por medicamento via regex (padrões como `1.1 NOME`, `1.2 NOME`, etc.).
- Cria `Document`s com metadados do título do medicamento.
- Gera embeddings com `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`).
- Cria/abre uma coleção Chroma (`bulas_poc`) e persiste os vetores no diretório `chroma_bulas_db/`.
- Inicializa duas instâncias do Gemini via `langchain-google-genai` (uma para RAG e outra para comparação sem RAG).
- Executa as consultas definidas em `consultas` e imprime resultados e tempos de execução.


### Estrutura do repositório

```
Extensao-3/
├─ chroma_bulas_db/           # Persistência do ChromaDB
├─ guia-medicamentos.pdf      # PDF de bulas (entrada)
├─ Prova de Conceito (POC) — Recuperação de Informações em Bulas de Medicamentos com LangChain e ChromaDB.docx
├─ test.py                    # Script principal da POC
└─ README.md                  # Este arquivo
```


### Limpeza/Reindexação

- Para recriar o índice do zero, apague o diretório `chroma_bulas_db/` e execute novamente o script.


### Solução de problemas (FAQ)

- O download do modelo `all-MiniLM-L6-v2` está lento: é normal na primeira execução. Aguarde o término; nas próximas rodadas será reutilizado do cache local.
- Erro de autenticação no Gemini: confirme se a chave foi inserida corretamente em `test.py` (ou se a variável de ambiente `GOOGLE_API_KEY` está setada) e se a conta tem acesso ao modelo configurado.
- Erros de import (`ModuleNotFoundError`): confira se o ambiente virtual está ativado e se todas as dependências foram instaladas sem erros.
- PDF não encontrado: verifique o caminho em `PDF_PATH` dentro de `test.py` (padrão: `guia-medicamentos.pdf`).


### Privacidade e custos

- O conteúdo do PDF é processado localmente; os textos recuperados podem ser enviados ao serviço do LLM (Gemini) para geração de respostas.
- O uso do Gemini pode gerar custos conforme sua conta do Google Cloud/AI Studio. Monitore sua utilização.


### Licença

Este repositório é apenas uma POC/estudo. Defina a licença conforme sua necessidade (ex.: MIT, Apache-2.0). Caso não informado, considere-o de uso interno.


