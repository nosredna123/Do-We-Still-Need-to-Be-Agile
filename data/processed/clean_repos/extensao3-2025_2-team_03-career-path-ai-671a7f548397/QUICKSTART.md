# 🚀 Quick Start - Career-Path-AI

## Executar o Projeto com Docker

### Opção 1: Usando o Script Automático (Recomendado)

```bash
# 1. Executar o script de configuração
./setup-env.sh

# 2. Iniciar os containers
docker compose up --build
```

### Opção 2: Configuração Manual

Se você já tem o arquivo `backend/.env` configurado:

1. **Criar `.env` na raiz:**
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais do PostgreSQL
   ```

2. **Criar `backend/.env.docker`:**
   ```bash
   cp backend/.env.docker.example backend/.env.docker
   # IMPORTANTE: Altere POSTGRES_HOST para "postgres" (nome do serviço Docker)
   ```

3. **Iniciar os containers:**
   ```bash
   docker compose up --build
   ```

## 📍 Acessos

Após iniciar os containers:

- **Frontend**: http://localhost:5173/login
- **Backend API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs

## 📚 Documentação Completa

- **Instalação detalhada**: Veja `SETUP_INSTALL.md`
- **Configuração Docker**: Veja `DOCKER_SETUP.md`

## ⚡ Comandos Rápidos

```bash
# Ver logs
docker compose logs -f

# Parar containers
docker compose stop

# Parar e remover containers
docker compose down

# Reiniciar um serviço
docker compose restart backend
```

