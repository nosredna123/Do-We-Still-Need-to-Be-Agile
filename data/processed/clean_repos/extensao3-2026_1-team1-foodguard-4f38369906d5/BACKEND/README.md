# Projeto Extensão

Este projeto utiliza o **VS Code Dev Containers** em conjunto com **Docker Compose** para garantir um ambiente de desenvolvimento isolado, padronizado e pronto para uso, contendo **Python (Django)** e **PostgreSQL**.

---

## Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas na sua máquina:

1. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: Recomendado usar com a integração WSL2 ativada (se estiver no Windows).
2. **[Visual Studio Code (VS Code)](https://code.visualstudio.com/)**.
3. **Extensão do VS Code**: [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (Instale na aba de extensões do VS Code).
4. **Git**.

## Configuração Inicial

1. **Clone o repositório:**
   `git clone https://github.com/VictorManoel-Timbo/extensao-3-projeto.git`
   `cd extensao-3-projeto`

2. **Variáveis de Ambiente:**
   Certifique-se de que a pasta `.envs/.local/` existe e contém o arquivo `.postgres` com as credenciais do banco de dados, pois o `docker-compose.local.yml` depende dele para subir o serviço.
   *Exemplo de `.envs/.local/.postgres`:*
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=nome_do_banco
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=sua_senha_segura

3. **Configuração do Git:**
   Para que o container não perca a sua identidade do Git a cada rebuild, nós utilizamos um script de inicialização (`setup.sh`).
   Crie um arquivo chamado `.git_config` dentro da pasta `.envs/.local/` com o seguinte formato:
   *Exemplo de `.envs/.local/.git_config`:*
   GIT_USER_NAME="Seu Nome Completo"
   GIT_USER_EMAIL="<seu_email@exemplo.com>"
   *(Nota: A pasta `.envs/` é ignorada pelo Git, mantendo seus dados seguros apenas na sua máquina local).*

4. **Iniciando o Container:**
   - Abra a pasta do projeto no VS Code.
   - Pressione `F1` (ou `Ctrl+Shift+P`), digite **`Dev Containers: Reopen in Container`** e aperte Enter.
   - O VS Code começará a construir a imagem Docker. A primeira vez pode demorar alguns minutos.

5. **Rodando o Servidor Django:**
   Dentro do terminal integrado do VS Code (que já estará dentro do Linux/Container), rode:
   `python manage.py runserver 0.0.0.0:8000`
   O app estará acessível no seu navegador em: `http://localhost:8000`

---

## Pre-commit

Utilizamos o `pre-commit` para garantir que todo o código enviado para o repositório siga os mesmos padrões de formatação e qualidade (removendo espaços em branco, formatando com *Black*, organizando imports com *isort*, etc).

### Rodando ANTES do `git push` (Recomendado)

Para evitar que seus commits sejam bloqueados na hora de enviar, é uma boa prática rodar o pre-commit manualmente em todos os arquivos **antes de commitar e fazer o push**:

`pre-commit run --all-files`

- Se a ferramenta encontrar erros ou arquivos fora do padrão, **ela corrigirá a maioria deles automaticamente**.
- Após a correção, os arquivos aparecerão como modificados. Basta adicioná-los novamente (`git add .`) e refazer o commit.
