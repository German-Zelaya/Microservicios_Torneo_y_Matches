#!/bin/bash

# Script para iniciar el GraphQL Gateway en modo desarrollo

echo "🚀 Iniciando GraphQL Gateway..."
echo ""

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js no está instalado"
    echo "Por favor, instala Node.js desde https://nodejs.org"
    exit 1
fi

# Verificar si las dependencias están instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
    echo ""
fi

# Verificar si existe el archivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Advertencia: No se encontró archivo .env"
    echo "📝 Creando .env con configuración por defecto..."
    cat > .env << EOF
PORT=4000
NODE_ENV=development

# Microservices URLs
TOURNAMENTS_SERVICE_URL=http://localhost:8001
MATCHES_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:3000
TEAMS_SERVICE_URL=http://localhost:3002
EOF
    echo "✅ Archivo .env creado"
    echo ""
fi

# Iniciar en modo desarrollo
echo "🎯 Iniciando servidor en modo desarrollo..."
echo ""
npm run dev
