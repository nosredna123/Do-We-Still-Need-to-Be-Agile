# Guia de Execução com Docker

Este guia explica como executar o projeto Career-Path-AI usando Docker Compose.

## Pré-requisitos

- Docker instalado
- Docker Compose instalado
- Chave de API do Google Gemini

## Configuração

### Arquivos de Configuração

O projeto já possui os arquivos de configuração necessários criados:

#### 1. `.env` (raiz do projeto)

Este arquivo contém as variáveis usadas pelo `docker-compose.yaml` para configurar o PostgreSQL:

```env
POSTGRES_DB=careerpath_db
POSTGRES_USER=careerpath_user
POSTGRES_PASSWORD=careerpath_pass
```

#### 2. `backend/.env.docker`

Este arquivo contém todas as configurações do backend que serão usadas dentro do container Docker:

- ✅ Database configurado (conecta ao serviço `postgres`)
- ✅ Email configurado
- ✅ Segurança configurada
- ✅ Gemini API Key configurada

**Importante**: 
- O `POSTGRES_HOST` está configurado como `postgres` (nome do serviço no docker-compose)
- Este é o valor correto para comunicação entre containers Docker
- Todas as configurações necessárias já estão presentes

## Execução

### 1. Construir e iniciar os containers

```bash
docker compose up --build
```

Este comando irá:
- Construir as imagens do backend e frontend
- Baixar a imagem do PostgreSQL 17
- Criar e iniciar todos os containers
- Executar as migrações do banco de dados automaticamente
- Iniciar os serviços

### 2. Parar os containers

Para parar os containers sem removê-los:

```bash
docker compose stop
```

### 3. Parar e remover containers

Para parar e remover os containers e volumes:

```bash
docker compose down
```

Para remover também os volumes (dados do banco):

```bash
docker compose down -v
```

### 4. Ver logs

Para ver os logs de todos os serviços:

```bash
docker compose logs -f
```

Para ver logs de um serviço específico:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### 5. Reiniciar um serviço específico

```bash
docker compose restart backend
docker compose restart frontend
docker compose restart postgres
```

## Acessos

Após iniciar os containers, acesse:

- **Frontend**: http://localhost:5173/login
- **Backend API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432

## Estrutura dos Serviços

### Backend
- **Container**: `career-path-backend`
- **Porta**: 8000
- **Comando**: Executa migrações Alembic e inicia o servidor Uvicorn
- **Variáveis**: Lê de `backend/.env.docker`

### Frontend
- **Container**: `career-path-frontend`
- **Porta**: 5173
- **Comando**: Executa `npm run dev -- --host`

### PostgreSQL
- **Container**: `career-path-postgres`
- **Porta**: 5432
- **Versão**: PostgreSQL 17
- **Volume**: `postgres_data` (persiste dados)
- **Healthcheck**: Configurado para aguardar o banco estar pronto

## Troubleshooting

### Erro de conexão com o banco

Se o backend não conseguir conectar ao PostgreSQL, verifique:
1. As credenciais no `.env` e `.env.docker` estão iguais
2. O `POSTGRES_HOST` no `.env.docker` está como `postgres`
3. O container do PostgreSQL está rodando: `docker compose ps`

### Erro de migração

Se houver erro nas migrações:
1. Verifique os logs: `docker compose logs backend`
2. As migrações são executadas automaticamente na inicialização
3. Para executar manualmente: `docker compose exec backend /app/.venv/bin/alembic upgrade head`

### Limpar tudo e começar do zero

```bash
# Parar e remover tudo
docker compose down -v

# Reconstruir e iniciar
docker compose up --build
```

### Verificar se os containers estão rodando

```bash
docker compose ps
```

### Acessar o shell do container

```bash
# Backend
docker compose exec backend sh

# Frontend
docker compose exec frontend sh

# PostgreSQL
docker compose exec postgres psql -U careerpath_user -d careerpath_db
```

## Desenvolvimento

Para desenvolvimento com hot-reload:

O frontend já está configurado com hot-reload usando Vite.

Para o backend, as mudanças em arquivos Python requerem rebuild do container ou você pode executar localmente conectando ao PostgreSQL do Docker.

## Volumes

- `postgres_data`: Persiste os dados do PostgreSQL entre reinicializações

## Rede

Todos os containers estão na mesma rede Docker e se comunicam pelo nome do serviço:
- Backend acessa PostgreSQL por `postgres:5432`
- Frontend acessa Backend por `backend:8000` (se necessário)

