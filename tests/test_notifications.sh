#!/bin/bash

# Script para probar el servicio de notificaciones

echo "🧪 =========================================="
echo "🧪 PRUEBA DE NOTIFICACIONES (SIMULADAS)"
echo "🧪 =========================================="
echo ""

NOTIFICATIONS_URL="http://localhost:3003"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Verificar que el servicio esté corriendo
echo -e "${YELLOW}📡 Verificando servicio de notificaciones...${NC}"
if curl -s ${NOTIFICATIONS_URL}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Notifications Service está disponible${NC}"
else
    echo -e "${RED}❌ Notifications Service no está disponible${NC}"
    echo "   Inicia el servicio con: docker compose up notifications-service"
    exit 1
fi

echo ""

# 2. Enviar notificación de prueba
echo -e "${BLUE}📧 Enviando notificación de prueba...${NC}"

curl -X POST ${NOTIFICATIONS_URL}/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-123",
    "type": "MATCH_REMINDER",
    "title": "¡Tu partido empieza pronto!",
    "message": "Tu partido contra TeamX comienza en 30 minutos. ¡Prepárate!",
    "metadata": {
      "matchId": "match-456",
      "tournamentId": "tournament-789"
    }
  }'

echo ""
echo ""

# 3. Ver logs del servicio
echo -e "${YELLOW}📋 Logs del servicio (últimas 20 líneas):${NC}"
docker logs notifications-service --tail 20

echo ""
echo -e "${GREEN}✅ Prueba completada${NC}"
echo ""
echo -e "${BLUE}💡 Notas:${NC}"
echo "   • Los emails se SIMULAN, no se envían realmente"
echo "   • Busca en los logs el mensaje: 📧 EMAIL SIMULADO ENVIADO"
echo "   • Ver logs completos: docker logs -f notifications-service"
