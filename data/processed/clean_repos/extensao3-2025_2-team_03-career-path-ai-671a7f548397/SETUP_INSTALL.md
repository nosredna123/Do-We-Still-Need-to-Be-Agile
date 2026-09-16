# Guia de Instalação e Execução - Career-Path-AI

Este guia explica como configurar e executar o projeto Career-Path-AI usando Docker.

## 📋 Pré-requisitos

- Docker instalado
- Docker Compose instalado
- Chave de API do Google Gemini (já configurada no `.env.docker`)

## 🚀 Instalação Rápida

### Passo 1: Verificar arquivos de configuração

O projeto já possui os arquivos de configuração necessários:

- ✅ `.env` (na raiz) - Configurações do PostgreSQL para o Docker Compose
- ✅ `backend/.env.docker` - Configurações do Backend para Docker

### Passo 2: Executar o projeto

```bash
docker compose up --build
```

Este comando irá:
1. Construir as imagens do backend e frontend
2. Baixar e iniciar o PostgreSQL 17
3. Executar as migrações do banco de dados automaticamente
4. Iniciar todos os serviços

### Passo 3: Acessar a aplicação

Após os containers iniciarem (pode levar alguns minutos na primeira vez), acesse:

- **Frontend**: http://localhost:5173/login
- **Backend API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Estrutura de Arquivos de Configuração

### `.env` (raiz do projeto)

Este arquivo contém as variáveis usadas pelo `docker-compose.yaml` para configurar o PostgreSQL:

```env
POSTGRES_DB=careerpath_db
POSTGRES_USER=careerpath_user
POSTGRES_PASSWORD=careerpath_pass
```

### `backend/.env.docker`

Este arquivo contém todas as configurações do backend que serão usadas dentro do container:

- Configurações do banco de dados (conecta ao serviço `postgres`)
- Configurações de email
- Chaves de segurança
- Chave da API do Google Gemini

**Importante**: O `POSTGRES_HOST` está configurado como `postgres`, que é o nome do serviço no docker-compose. Isso permite que o backend se conecte ao PostgreSQL através da rede Docker.

## 🛠️ Comandos Úteis

### Ver logs dos serviços

```bash
# Todos os serviços
docker compose logs -f

# Apenas backend
docker compose logs -f backend

# Apenas frontend
docker compose logs -f frontend

# Apenas PostgreSQL
docker compose logs -f postgres
```

### Parar os serviços

```bash
# Parar sem remover containers
docker compose stop

# Parar e remover containers
docker compose down

# Parar, remover containers e volumes (apaga dados do banco)
docker compose down -v
```

### Reiniciar um serviço específico

```bash
docker compose restart backend
docker compose restart frontend
docker compose restart postgres
```

### Verificar status dos containers

```bash
docker compose ps
```

### Acessar shell dos containers

```bash
# Backend
docker compose exec backend sh

# Frontend
docker compose exec frontend sh

# PostgreSQL
docker compose exec postgres psql -U careerpath_user -d careerpath_db
```

## 🔧 Troubleshooting

### Erro: "Cannot connect to database"

**Problema**: O backend não consegue conectar ao PostgreSQL.

**Solução**:
1. Verifique se o container do PostgreSQL está rodando: `docker compose ps`
2. Verifique se as credenciais em `.env` e `backend/.env.docker` estão iguais
3. Certifique-se de que `POSTGRES_HOST=postgres` no `backend/.env.docker`
4. Veja os logs: `docker compose logs postgres`

### Erro: "Migration failed"

**Problema**: Erro ao executar migrações do banco.

**Solução**:
1. Veja os logs do backend: `docker compose logs backend`
2. Execute as migrações manualmente:
   ```bash
   docker compose exec backend /app/.venv/bin/alembic upgrade head
   ```

### Erro: "Port already in use"

**Problema**: Porta 8000, 5173 ou 5432 já está em uso.

**Solução**:
1. Pare o serviço que está usando a porta
2. Ou altere as portas no `docker-compose.yaml`

### Limpar tudo e recomeçar

```bash
# Para tudo e remove volumes
docker compose down -v

# Remove imagens antigas (opcional)
docker system prune -a

# Reconstruir e iniciar
docker compose up --build
```

### Ver logs de erro específicos

```bash
# Erros do backend
docker compose logs backend | grep -i error

# Erros do frontend
docker compose logs frontend | grep -i error
```

## 📝 Notas Importantes

1. **Primeira execução**: A primeira vez que executar `docker compose up --build` pode levar alguns minutos para baixar imagens e construir containers.

2. **Dados persistidos**: Os dados do PostgreSQL são salvos em um volume Docker chamado `postgres_data`. Mesmo que você pare os containers, os dados são mantidos.

3. **Hot-reload**: 
   - O frontend tem hot-reload habilitado (mudanças são refletidas automaticamente)
   - Para mudanças no backend, é necessário reconstruir o container ou executar localmente

4. **Variáveis sensíveis**: 
   - As chaves de API e senhas estão nos arquivos `.env` e `.env.docker`
   - Esses arquivos são ignorados pelo git (`.gitignore`)
   - **Nunca commite** esses arquivos no repositório

## 🔄 Atualizando Configurações

Se precisar atualizar as configurações:

1. Edite o arquivo correspondente (`.env` ou `backend/.env.docker`)
2. Reinicie os serviços:
   ```bash
   docker compose restart backend
   # ou
   docker compose down && docker compose up -d
   ```

## 📚 Documentação Adicional

- Para mais detalhes sobre a estrutura do projeto, veja `DOCKER_SETUP.md`
- Para documentação da API, acesse http://localhost:8000/docs após iniciar os containers

