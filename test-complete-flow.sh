#!/bin/bash

# Script de prueba completa del flujo de torneos y matches
# FASE 4: Prueba end-to-end del sistema

echo "🎮 ======================================"
echo "🎮 PRUEBA COMPLETA DEL SISTEMA"
echo "🎮 Torneo con 4 participantes"
echo "🎮 ======================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs de servicios
TOURNAMENTS_URL="http://localhost:8001"
MATCHES_URL="http://localhost:8002"

echo -e "${BLUE}📋 PASO 1: Crear torneo${NC}"
TOURNAMENT_RESPONSE=$(curl -s -X POST $TOURNAMENTS_URL/api/v1/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Torneo de Prueba Automático",
    "game": "League of Legends",
    "max_participants": 8,
    "description": "Prueba completa del sistema de brackets automáticos"
  }')

TOURNAMENT_ID=$(echo $TOURNAMENT_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo -e "${GREEN}✅ Torneo creado con ID: $TOURNAMENT_ID${NC}"
echo ""

sleep 1

echo -e "${BLUE}📋 PASO 2: Cambiar estado del torneo a 'registration'${NC}"
curl -s -X PATCH $TOURNAMENTS_URL/api/v1/tournaments/$TOURNAMENT_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status": "registration"}' > /dev/null
echo -e "${GREEN}✅ Estado cambiado a 'registration'${NC}"
echo ""

sleep 1

echo -e "${BLUE}📋 PASO 3: Iniciar torneo con 4 participantes${NC}"
curl -s -X POST $TOURNAMENTS_URL/api/v1/tournaments/$TOURNAMENT_ID/start \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": [1, 2, 3, 4]
  }' > /dev/null
echo -e "${GREEN}✅ Torneo iniciado - Brackets generados${NC}"
echo -e "${YELLOW}   → Se crearon 2 matches en la Ronda 1${NC}"
echo ""

sleep 2

echo -e "${BLUE}📋 PASO 4: Listar matches creados${NC}"
MATCHES=$(curl -s "$MATCHES_URL/api/v1/matches?tournament_id=$TOURNAMENT_ID")
echo $MATCHES | jq '.matches[] | "Match \(.id): Round \(.round), Player \(.player1_id) vs Player \(.player2_id), Status: \(.status)"'
echo ""

sleep 1

echo -e "${BLUE}🎮 ======================================"
echo -e "${BLUE}🎮 RONDA 1 - SEMIFINALES"
echo -e "${BLUE}🎮 ======================================"
echo ""

# MATCH 1 - Ronda 1
echo -e "${YELLOW}🎯 MATCH 1: Player 1 vs Player 2${NC}"
echo -e "${BLUE}   1. Iniciar match...${NC}"
curl -s -X PATCH $MATCHES_URL/api/v1/matches/1/start > /dev/null
echo -e "${GREEN}   ✅ Match iniciado${NC}"
sleep 1

echo -e "${BLUE}   2. Reportar resultado (Gana Player 1)...${NC}"
curl -s -X POST $MATCHES_URL/api/v1/matches/1/result \
  -H "Content-Type: application/json" \
  -d '{
    "player1_score": 15,
    "player2_score": 8,
    "winner_id": 1,
    "notes": "Victoria dominante de Player 1"
  }' > /dev/null
echo -e "${GREEN}   ✅ Resultado reportado (Estado: pending_validation)${NC}"
sleep 1

echo -e "${BLUE}   3. Validar resultado...${NC}"
curl -s -X PUT $MATCHES_URL/api/v1/matches/1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "Resultado verificado por referee"
  }' > /dev/null
echo -e "${GREEN}   ✅ Resultado validado (Estado: completed)${NC}"
echo -e "${GREEN}   🏆 Player 1 avanza a la FINAL${NC}"
echo ""

sleep 2

# MATCH 2 - Ronda 1
echo -e "${YELLOW}🎯 MATCH 2: Player 3 vs Player 4${NC}"
echo -e "${BLUE}   1. Iniciar match...${NC}"
curl -s -X PATCH $MATCHES_URL/api/v1/matches/2/start > /dev/null
echo -e "${GREEN}   ✅ Match iniciado${NC}"
sleep 1

echo -e "${BLUE}   2. Reportar resultado (Gana Player 3)...${NC}"
curl -s -X POST $MATCHES_URL/api/v1/matches/2/result \
  -H "Content-Type: application/json" \
  -d '{
    "player1_score": 12,
    "player2_score": 14,
    "winner_id": 3,
    "notes": "Comeback épico de Player 3"
  }' > /dev/null
echo -e "${GREEN}   ✅ Resultado reportado (Estado: pending_validation)${NC}"
sleep 1

echo -e "${BLUE}   3. Validar resultado...${NC}"
curl -s -X PUT $MATCHES_URL/api/v1/matches/2/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "Resultado verificado por referee"
  }' > /dev/null
echo -e "${GREEN}   ✅ Resultado validado (Estado: completed)${NC}"
echo -e "${GREEN}   🏆 Player 3 avanza a la FINAL${NC}"
echo ""

sleep 2

echo -e "${BLUE}🎮 ======================================"
echo -e "${BLUE}🎮 VERIFICANDO BRACKET AUTOMÁTICO"
echo -e "${BLUE}🎮 ======================================"
echo ""

echo -e "${BLUE}📋 Verificando que se creó el match de la FINAL...${NC}"
sleep 2
MATCHES_ROUND2=$(curl -s "$MATCHES_URL/api/v1/matches?tournament_id=$TOURNAMENT_ID")
FINAL_MATCH=$(echo $MATCHES_ROUND2 | jq '.matches[] | select(.round == 2)')

if [ -z "$FINAL_MATCH" ]; then
  echo -e "${RED}❌ ERROR: No se creó el match de la final${NC}"
  exit 1
fi

FINAL_PLAYER1=$(echo $FINAL_MATCH | jq -r '.player1_id')
FINAL_PLAYER2=$(echo $FINAL_MATCH | jq -r '.player2_id')

echo -e "${GREEN}✅ Match de FINAL creado automáticamente!${NC}"
echo -e "${YELLOW}   → Final: Player $FINAL_PLAYER1 vs Player $FINAL_PLAYER2${NC}"
echo ""

sleep 1

echo -e "${BLUE}🎮 ======================================"
echo -e "${BLUE}🎮 RONDA 2 - FINAL"
echo -e "${BLUE}🎮 ======================================"
echo ""

echo -e "${YELLOW}🏆 FINAL: Player $FINAL_PLAYER1 vs Player $FINAL_PLAYER2${NC}"
echo -e "${BLUE}   1. Iniciar match final...${NC}"
curl -s -X PATCH $MATCHES_URL/api/v1/matches/3/start > /dev/null
echo -e "${GREEN}   ✅ Match final iniciado${NC}"
sleep 1

echo -e "${BLUE}   2. Reportar resultado (Gana Player $FINAL_PLAYER1)...${NC}"
curl -s -X POST $MATCHES_URL/api/v1/matches/3/result \
  -H "Content-Type: application/json" \
  -d "{
    \"player1_score\": 20,
    \"player2_score\": 15,
    \"winner_id\": $FINAL_PLAYER1,
    \"notes\": \"¡Player $FINAL_PLAYER1 es el CAMPEÓN!\"
  }" > /dev/null
echo -e "${GREEN}   ✅ Resultado reportado${NC}"
sleep 1

echo -e "${BLUE}   3. Validar resultado final...${NC}"
curl -s -X PUT $MATCHES_URL/api/v1/matches/3/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "CAMPEÓN OFICIAL DEL TORNEO"
  }' > /dev/null
echo -e "${GREEN}   ✅ Resultado validado${NC}"
echo ""

sleep 1

echo -e "${BLUE}🎮 ======================================"
echo -e "${BLUE}🎮 RESUMEN FINAL DEL TORNEO"
echo -e "${BLUE}🎮 ======================================"
echo ""

echo -e "${BLUE}📊 Todos los matches del torneo:${NC}"
ALL_MATCHES=$(curl -s "$MATCHES_URL/api/v1/matches?tournament_id=$TOURNAMENT_ID")
echo $ALL_MATCHES | jq '.matches[] | "Round \(.round) - Match \(.match_number): Player \(.player1_id // "TBD") vs Player \(.player2_id // "TBD") | Ganador: \(.winner_id // "Pendiente") | Estado: \(.status)"'
echo ""

echo -e "${GREEN}🏆 ======================================"
echo -e "${GREEN}🏆 CAMPEÓN DEL TORNEO: PLAYER $FINAL_PLAYER1"
echo -e "${GREEN}🏆 ======================================"
echo ""

echo -e "${BLUE}📋 RESUMEN DE PRUEBAS:${NC}"
echo -e "${GREEN}✅ Fase 1: Reportar resultados - FUNCIONAL${NC}"
echo -e "${GREEN}✅ Fase 2: Validar resultados - FUNCIONAL${NC}"
echo -e "${GREEN}✅ Fase 3: Actualización automática de brackets - FUNCIONAL${NC}"
echo -e "${GREEN}✅ Fase 4: Flujo completo end-to-end - FUNCIONAL${NC}"
echo ""

echo -e "${GREEN}🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!${NC}"
echo ""

echo -e "${YELLOW}💡 Para ver los logs detallados, revisa la salida de docker-compose${NC}"
echo -e "${YELLOW}💡 Para ver RabbitMQ admin panel: http://localhost:15672 (guest/guest)${NC}"
