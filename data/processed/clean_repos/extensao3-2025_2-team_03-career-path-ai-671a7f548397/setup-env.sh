#!/bin/bash

# Script para criar os arquivos .env necessários baseados nos valores do backend/.env existente

echo "🔧 Configurando arquivos de ambiente para Docker..."

# Verifica se backend/.env existe
if [ ! -f "backend/.env" ]; then
    echo "❌ Erro: backend/.env não encontrado!"
    echo "   Por favor, crie o arquivo backend/.env primeiro."
    exit 1
fi

# Cria .env na raiz se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando .env na raiz..."
    cat > .env << EOF
# Variáveis de ambiente para o Docker Compose
# Gerado automaticamente em $(date)

POSTGRES_DB=careerpath_db
POSTGRES_USER=careerpath_user
POSTGRES_PASSWORD=careerpath_pass
EOF
    echo "✅ Arquivo .env criado na raiz"
else
    echo "ℹ️  Arquivo .env já existe na raiz"
fi

# Cria backend/.env.docker baseado no backend/.env
echo "📝 Criando backend/.env.docker..."

# Lê valores do backend/.env
POSTGRES_DB=$(grep "^POSTGRES_DB=" backend/.env | cut -d '=' -f2 | tr -d ' ')
POSTGRES_USER=$(grep "^POSTGRES_USER=" backend/.env | cut -d '=' -f2 | tr -d ' ')
POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" backend/.env | cut -d '=' -f2 | tr -d ' ')
FRONTEND_HOST=$(grep "^FRONTEND_HOST=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "http://localhost:5173")
MAIL_USERNAME=$(grep "^MAIL_USERNAME=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "")
MAIL_PASSWORD=$(grep "^MAIL_PASSWORD=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "")
MAIL_PORT=$(grep "^MAIL_PORT=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "587")
MAIL_SERVER=$(grep "^MAIL_SERVER=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "smtp.gmail.com")
MAIL_STARTTLS=$(grep "^MAIL_STARTTLS=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "True")
MAIL_SSL_TLS=$(grep "^MAIL_SSL_TLS=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "False")
MAIL_FROM=$(grep "^MAIL_FROM=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "")
USE_CREDENTIALS=$(grep "^USE_CREDENTIALS=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "True")
DEBUG=$(grep "^DEBUG=" backend/.env | cut -d '=' -f2 | tr -d ' ' | head -1 || echo "True")
SECRET_KEY=$(grep "^SECRET_KEY=" backend/.env | cut -d '=' -f2 | tr -d ' ' | head -1 || echo "")
ALGORITHM=$(grep "^ALGORITHM=" backend/.env | cut -d '=' -f2 | tr -d ' ' | head -1 || echo "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES=$(grep "^ACCESS_TOKEN_EXPIRE_MINUTES=" backend/.env | cut -d '=' -f2 | tr -d ' ' | head -1 || echo "30")
GEMINI_API_KEY=$(grep "^GEMINI_API_KEY=" backend/.env | cut -d '=' -f2 | tr -d ' ' || echo "")

# Cria o arquivo .env.docker
cat > backend/.env.docker << EOF
# Variáveis de ambiente para o Backend no Docker
# Gerado automaticamente em $(date)
# IMPORTANTE: POSTGRES_HOST deve ser "postgres" (nome do serviço no docker-compose)

# Database
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Frontend
FRONTEND_HOST=${FRONTEND_HOST}

# Email
MAIL_USERNAME=${MAIL_USERNAME}
MAIL_PASSWORD=${MAIL_PASSWORD}
MAIL_PORT=${MAIL_PORT}
MAIL_SERVER=${MAIL_SERVER}
MAIL_STARTTLS=${MAIL_STARTTLS}
MAIL_SSL_TLS=${MAIL_SSL_TLS}
MAIL_FROM=${MAIL_FROM}
USE_CREDENTIALS=${USE_CREDENTIALS}

# Application
DEBUG=${DEBUG}
SECRET_KEY=${SECRET_KEY}
ALGORITHM=${ALGORITHM}
ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}

# Gemini AI
GEMINI_API_KEY=${GEMINI_API_KEY}
EOF

echo "✅ Arquivo backend/.env.docker criado"
echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "Agora você pode executar:"
echo "  docker compose up --build"
echo ""

