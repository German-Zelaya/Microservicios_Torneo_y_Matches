#!/bin/bash

# Script de prueba para el GraphQL Gateway

echo "🧪 Probando GraphQL Gateway..."
echo ""

GATEWAY_URL="http://localhost:4000"

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para hacer queries GraphQL
graphql_query() {
    local query=$1
    curl -s -X POST "${GATEWAY_URL}/graphql" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"${query}\"}"
}

# 1. Health Check
echo "1️⃣  Health Check del Gateway..."
response=$(curl -s "${GATEWAY_URL}/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Gateway está funcionando${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
else
    echo -e "${RED}❌ Gateway no responde${NC}"
    echo "Asegúrate de que el Gateway esté corriendo en el puerto 4000"
    exit 1
fi
echo ""

# 2. Health Check de servicios
echo "2️⃣  Verificando conexión con servicios..."
query="query { health healthTournaments healthMatches }"
response=$(graphql_query "$query")
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

# 3. Listar torneos
echo "3️⃣  Listando torneos..."
query="query { tournaments(page: 1, page_size: 5) { total tournaments { id name game status } } }"
response=$(graphql_query "$query")
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

# 4. Crear un torneo de prueba
echo "4️⃣  Creando torneo de prueba..."
query="mutation { createTournament(input: { name: \\\"Test GraphQL Tournament\\\", game: \\\"Test Game\\\", max_participants: 8, tournament_type: individual }) { id name game status } }"
response=$(graphql_query "$query")
echo "$response" | jq '.' 2>/dev/null || echo "$response"

# Extraer el ID del torneo creado
tournament_id=$(echo "$response" | jq -r '.data.createTournament.id' 2>/dev/null)

if [ ! -z "$tournament_id" ] && [ "$tournament_id" != "null" ]; then
    echo -e "${GREEN}✅ Torneo creado con ID: $tournament_id${NC}"
    echo ""
    
    # 5. Obtener el torneo creado
    echo "5️⃣  Obteniendo detalles del torneo..."
    query="query { tournament(id: $tournament_id) { id name game status max_participants tournament_type created_at } }"
    response=$(graphql_query "$query")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
    
    # 6. Actualizar el torneo
    echo "6️⃣  Actualizando torneo..."
    query="mutation { updateTournament(id: $tournament_id, input: { description: \\\"Torneo actualizado via GraphQL\\\" }) { id description } }"
    response=$(graphql_query "$query")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
    
    # 7. Cambiar estado a registration
    echo "7️⃣  Cambiando estado a 'registration'..."
    query="mutation { changeTournamentStatus(id: $tournament_id, status: registration) { id status } }"
    response=$(graphql_query "$query")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
    
    # 8. Limpiar - eliminar torneo de prueba
    echo "8️⃣  Limpiando - eliminando torneo de prueba..."
    query="mutation { deleteTournament(id: $tournament_id) }"
    response=$(graphql_query "$query")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
else
    echo -e "${YELLOW}⚠️  No se pudo crear el torneo. Puede que el servicio de torneos no esté disponible.${NC}"
    echo ""
fi

# 9. Listar matches
echo "9️⃣  Listando matches..."
query="query { matches { total matches { id status tournament_id } } }"
response=$(graphql_query "$query")
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

echo -e "${GREEN}✅ Pruebas completadas!${NC}"
echo ""
echo "📚 Para más ejemplos, consulta:"
echo "   - graphql-gateway/EXAMPLES.md"
echo "   - graphql-gateway/GETTING_STARTED.md"
echo ""
echo "🌐 Apollo Studio Explorer:"
echo "   http://localhost:4000/graphql"
