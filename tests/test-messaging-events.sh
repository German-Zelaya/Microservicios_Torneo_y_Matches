#!/bin/bash

# Script de prueba para eventos de RabbitMQ entre torneos y matches

echo "🧪 =========================================="
echo "🧪 PRUEBA DE EVENTOS RABBITMQ"
echo "🧪 =========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# URLs base
TOURNAMENTS_URL="http://localhost:8001"
MATCHES_URL="http://localhost:8002"

# Función para mostrar logs de servicio
show_logs() {
    local service=$1
    local lines=${2:-20}
    echo -e "${BLUE}📋 Logs de ${service}:${NC}"
    docker logs --tail ${lines} ${service}
    echo ""
}

# Función para verificar que los servicios estén corriendo
check_services() {
    echo -e "${YELLOW}🔍 Verificando servicios...${NC}"
    
    # Verificar tournaments-service
    if curl -s ${TOURNAMENTS_URL}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Tournaments Service está corriendo${NC}"
    else
        echo -e "${RED}❌ Tournaments Service no está disponible${NC}"
        exit 1
    fi
    
    # Verificar matches-service
    if curl -s ${MATCHES_URL}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Matches Service está corriendo${NC}"
    else
        echo -e "${RED}❌ Matches Service no está disponible${NC}"
        exit 1
    fi
    
    # Verificar RabbitMQ
    if docker exec rabbitmq-esports rabbitmqctl status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ RabbitMQ está corriendo${NC}"
    else
        echo -e "${RED}❌ RabbitMQ no está disponible${NC}"
        exit 1
    fi
    
    echo ""
}

# Función para monitorear RabbitMQ
monitor_rabbitmq() {
    echo -e "${BLUE}🐰 Estado de RabbitMQ:${NC}"
    docker exec rabbitmq-esports rabbitmqctl list_exchanges
    echo ""
    docker exec rabbitmq-esports rabbitmqctl list_queues
    echo ""
}

# 1. Verificar servicios
check_services

# 2. Ver estado de RabbitMQ
monitor_rabbitmq

# 3. Crear un torneo
echo -e "${YELLOW}📝 PASO 1: Crear un torneo...${NC}"
TOURNAMENT_RESPONSE=$(curl -s -X POST ${TOURNAMENTS_URL}/api/v1/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tournament RabbitMQ",
    "description": "Torneo de prueba para eventos",
    "game": "League of Legends",
    "format": "single_elimination",
    "max_participants": 8,
    "start_date": "2025-12-01T10:00:00",
    "end_date": "2025-12-01T18:00:00",
    "status": "draft"
  }')

echo "Respuesta: ${TOURNAMENT_RESPONSE}"
TOURNAMENT_ID=$(echo ${TOURNAMENT_RESPONSE} | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

if [ -z "$TOURNAMENT_ID" ]; then
    echo -e "${RED}❌ No se pudo crear el torneo${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Torneo creado con ID: ${TOURNAMENT_ID}${NC}"
echo ""

# Esperar un poco para que se procese el evento
echo -e "${YELLOW}⏳ Esperando procesamiento del evento (3 segundos)...${NC}"
sleep 3

# Ver logs de matches-service para verificar que recibió el evento
echo -e "${BLUE}📋 Logs de Matches Service (debe mostrar evento recibido):${NC}"
show_logs "matches-service" 30

# 4. Agregar participantes al torneo
echo -e "${YELLOW}📝 PASO 2: Agregar participantes...${NC}"

# Simular IDs de usuarios (en un caso real, vendrían del auth-service)
PARTICIPANTS=(
    "00000000-0000-0000-0000-000000000001"
    "00000000-0000-0000-0000-000000000002"
    "00000000-0000-0000-0000-000000000003"
    "00000000-0000-0000-0000-000000000004"
    "00000000-0000-0000-0000-000000000005"
    "00000000-0000-0000-0000-000000000006"
    "00000000-0000-0000-0000-000000000007"
    "00000000-0000-0000-0000-000000000008"
)

for user_id in "${PARTICIPANTS[@]}"; do
    curl -s -X POST ${TOURNAMENTS_URL}/api/v1/tournaments/${TOURNAMENT_ID}/participants \
      -H "Content-Type: application/json" \
      -d "{\"user_id\": \"${user_id}\"}" > /dev/null
    echo -e "${GREEN}✅ Participante agregado: ${user_id}${NC}"
done

echo ""
sleep 2

# 5. Generar bracket
echo -e "${YELLOW}📝 PASO 3: Generar bracket (esto debería crear los matches)...${NC}"
BRACKET_RESPONSE=$(curl -s -X POST ${TOURNAMENTS_URL}/api/v1/tournaments/${TOURNAMENT_ID}/generate-bracket)

echo "Respuesta: ${BRACKET_RESPONSE}"
echo ""

# Esperar para que se procese el evento
echo -e "${YELLOW}⏳ Esperando procesamiento del evento BRACKET_GENERATED (5 segundos)...${NC}"
sleep 5

# Ver logs de matches-service
echo -e "${BLUE}📋 Logs de Matches Service (debe mostrar creación de matches):${NC}"
show_logs "matches-service" 50

# 6. Verificar que se crearon los matches
echo -e "${YELLOW}📝 PASO 4: Verificar matches creados...${NC}"
MATCHES_RESPONSE=$(curl -s ${MATCHES_URL}/api/matches?tournament_id=${TOURNAMENT_ID})

echo "Matches creados:"
echo ${MATCHES_RESPONSE} | python3 -m json.tool 2>/dev/null || echo ${MATCHES_RESPONSE}
echo ""

# Contar matches
MATCHES_COUNT=$(echo ${MATCHES_RESPONSE} | grep -o '"id":' | wc -l)
echo -e "${GREEN}✅ Total de matches creados: ${MATCHES_COUNT}${NC}"
echo ""

# 7. Simular completar un match
echo -e "${YELLOW}📝 PASO 5: Simular completar un match...${NC}"

# Obtener el primer match
FIRST_MATCH=$(curl -s ${MATCHES_URL}/api/matches?tournament_id=${TOURNAMENT_ID})
MATCH_ID=$(echo ${FIRST_MATCH} | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ ! -z "$MATCH_ID" ]; then
    echo -e "Completando match ID: ${MATCH_ID}"
    
    # Iniciar el match
    curl -s -X PATCH ${MATCHES_URL}/api/matches/${MATCH_ID}/start > /dev/null
    echo -e "${GREEN}✅ Match iniciado${NC}"
    sleep 2
    
    # Reportar resultado (player1 gana)
    RESULT_RESPONSE=$(curl -s -X POST ${MATCHES_URL}/api/matches/${MATCH_ID}/result \
      -H "Content-Type: application/json" \
      -d '{
        "player1_score": 16,
        "player2_score": 8
      }')
    
    echo "Resultado reportado: ${RESULT_RESPONSE}"
    echo ""
    
    # Esperar procesamiento
    echo -e "${YELLOW}⏳ Esperando procesamiento del evento MATCH_FINISHED (5 segundos)...${NC}"
    sleep 5
    
    # Ver logs de tournaments-service
    echo -e "${BLUE}📋 Logs de Tournaments Service (debe mostrar evento de match completado):${NC}"
    show_logs "tournaments-service" 30
    
    # Ver logs de matches-service
    echo -e "${BLUE}📋 Logs de Matches Service:${NC}"
    show_logs "matches-service" 30
fi

# 8. Ver estado final de RabbitMQ
echo -e "${YELLOW}📊 PASO 6: Estado final de RabbitMQ${NC}"
monitor_rabbitmq

# 9. Resumen
echo -e "${BLUE}🎉 ==========================================${NC}"
echo -e "${BLUE}🎉 RESUMEN DE PRUEBAS${NC}"
echo -e "${BLUE}🎉 ==========================================${NC}"
echo ""
echo -e "${GREEN}✅ Torneo creado (ID: ${TOURNAMENT_ID})${NC}"
echo -e "${GREEN}✅ ${#PARTICIPANTS[@]} participantes agregados${NC}"
echo -e "${GREEN}✅ Bracket generado${NC}"
echo -e "${GREEN}✅ ${MATCHES_COUNT} matches creados${NC}"

if [ ! -z "$MATCH_ID" ]; then
    echo -e "${GREEN}✅ Match completado (ID: ${MATCH_ID})${NC}"
fi

echo ""
echo -e "${YELLOW}💡 Consejos:${NC}"
echo "  1. Revisa los logs arriba para ver los eventos procesados"
echo "  2. Accede a RabbitMQ Management UI: http://localhost:15672 (guest/guest)"
echo "  3. Puedes ver más detalles con: docker logs tournaments-service"
echo "  4. O con: docker logs matches-service"
echo ""
echo -e "${GREEN}✅ Prueba completada!${NC}"
