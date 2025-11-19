#!/bin/bash

# Script para monitorear eventos de RabbitMQ en tiempo real

echo "🎯 =========================================="
echo "🎯 MONITOR DE EVENTOS RABBITMQ EN VIVO"
echo "🎯 =========================================="
echo ""
echo "📡 Monitoreando logs de ambos servicios..."
echo "   • Tournaments Service (Python) - Eventos publicados"
echo "   • Matches Service (Go) - Eventos recibidos"
echo ""
echo "💡 Presiona Ctrl+C para detener"
echo ""
echo "🎬 Iniciando en 3 segundos..."
sleep 3
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Función para procesar logs de tournaments
process_tournaments_logs() {
    docker logs -f tournaments-service 2>&1 | while read line; do
        if echo "$line" | grep -q "📤"; then
            echo -e "${MAGENTA}[TOURNAMENTS]${NC} ${line}"
        elif echo "$line" | grep -q "Evento publicado"; then
            echo -e "${MAGENTA}[TOURNAMENTS]${NC} ${line}"
        fi
    done
}

# Función para procesar logs de matches
process_matches_logs() {
    docker logs -f matches-service 2>&1 | while read line; do
        if echo "$line" | grep -q "📩"; then
            echo -e "${CYAN}[MATCHES]${NC} ${line}"
        elif echo "$line" | grep -qE "Evento recibido|Torneo creado|actualizado|eliminado|Estado.*cambiado"; then
            echo -e "${CYAN}[MATCHES]${NC} ${line}"
        fi
    done
}

# Ejecutar ambos en paralelo
process_tournaments_logs &
PID1=$!

process_matches_logs &
PID2=$!

# Esperar señal de interrupción
trap "echo ''; echo '👋 Deteniendo monitor...'; kill $PID1 $PID2 2>/dev/null; exit 0" INT

wait
