#!/bin/bash

# Script para visualizar logs centralizados de microservicios
# Uso: ./view-logs.sh [opciones]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  📋 Script de Visualización de Logs Centralizados${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Uso:${NC}"
    echo "  ./view-logs.sh [opción]"
    echo ""
    echo -e "${YELLOW}Opciones:${NC}"
    echo "  all                  - Ver logs de TODOS los servicios (por defecto)"
    echo "  services             - Ver logs solo de microservicios"
    echo "  databases            - Ver logs solo de bases de datos"
    echo "  infrastructure       - Ver logs de cache y mensajería"
    echo ""
    echo "  tournaments          - Ver logs del servicio de torneos"
    echo "  matches              - Ver logs del servicio de partidos"
    echo "  auth                 - Ver logs del servicio de autenticación"
    echo "  teams                - Ver logs del servicio de equipos"
    echo "  notifications        - Ver logs del servicio de notificaciones"
    echo ""
    echo "  postgres             - Ver logs de PostgreSQL"
    echo "  mongodb              - Ver logs de MongoDB"
    echo "  redis                - Ver logs de Redis"
    echo "  rabbitmq             - Ver logs de RabbitMQ"
    echo ""
    echo "  follow <servicio>    - Seguir logs en tiempo real de un servicio"
    echo "  errors               - Ver solo ERRORES de todos los servicios"
    echo "  stats                - Ver estadísticas de logs"
    echo "  clean                - Limpiar logs antiguos (requiere confirmación)"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  ./view-logs.sh services"
    echo "  ./view-logs.sh tournaments"
    echo "  ./view-logs.sh follow matches"
    echo "  ./view-logs.sh errors"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
}

# Función para verificar que Docker esté corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Error: Docker no está corriendo${NC}"
        exit 1
    fi
}

# Función para mostrar logs con color según el servicio
show_logs() {
    local service=$1
    local lines=${2:-100}
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📝 Logs de: ${YELLOW}$service${NC} (últimas $lines líneas)"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    docker compose logs --tail=$lines $service 2>/dev/null || echo -e "${RED}❌ Servicio no encontrado o no está corriendo${NC}"
    echo ""
}

# Función para seguir logs en tiempo real
follow_logs() {
    local service=$1
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📺 Siguiendo logs de: ${YELLOW}$service${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}Presiona Ctrl+C para detener${NC}"
    echo ""
    docker compose logs -f $service
}

# Función para mostrar solo errores
show_errors() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  ERRORES DETECTADOS EN LOS LOGS${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    docker compose logs --tail=500 2>/dev/null | grep -iE "error|exception|failed|fatal|panic|critical" --color=always || echo -e "${GREEN}✅ No se encontraron errores recientes${NC}"
}

# Función para mostrar estadísticas
show_stats() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📊 ESTADÍSTICAS DE LOGS${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    echo -e "${YELLOW}Contenedores activos:${NC}"
    docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null
    echo ""
    
    echo -e "${YELLOW}Tamaño de logs por servicio:${NC}"
    for container in $(docker compose ps -q 2>/dev/null); do
        local name=$(docker inspect --format='{{.Name}}' $container | sed 's/^\/\|esports-//g')
        local log_file=$(docker inspect --format='{{.LogPath}}' $container)
        if [ -f "$log_file" ]; then
            local size=$(du -h "$log_file" | cut -f1)
            echo -e "  ${GREEN}$name:${NC} $size"
        fi
    done
    echo ""
    
    echo -e "${YELLOW}Conteo de logs por nivel (últimas 1000 líneas):${NC}"
    docker compose logs --tail=1000 2>/dev/null | grep -io "error\|warning\|info\|debug" | sort | uniq -c | sort -rn
    echo ""
}

# Función para limpiar logs
clean_logs() {
    echo -e "${YELLOW}⚠️  Advertencia: Esto eliminará los logs de todos los contenedores${NC}"
    read -p "¿Estás seguro? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo -e "${BLUE}🧹 Limpiando logs...${NC}"
        docker compose down 2>/dev/null
        docker system prune --volumes -f
        echo -e "${GREEN}✅ Logs limpiados${NC}"
        echo -e "${BLUE}💡 Puedes reiniciar los servicios con: docker compose up -d${NC}"
    else
        echo -e "${RED}❌ Operación cancelada${NC}"
    fi
}

# Main
main() {
    check_docker
    
    case "${1:-all}" in
        help|-h|--help)
            show_help
            ;;
        all)
            echo -e "${GREEN}📋 Mostrando logs de TODOS los servicios${NC}"
            docker compose logs --tail=100
            ;;
        services)
            echo -e "${GREEN}📋 Mostrando logs de MICROSERVICIOS${NC}"
            docker compose logs --tail=100 tournaments-service matches-service auth-service teams-service notifications-service
            ;;
        databases)
            echo -e "${GREEN}📋 Mostrando logs de BASES DE DATOS${NC}"
            docker compose logs --tail=100 postgres mongodb
            ;;
        infrastructure)
            echo -e "${GREEN}📋 Mostrando logs de INFRAESTRUCTURA${NC}"
            docker compose logs --tail=100 redis rabbitmq
            ;;
        tournaments)
            show_logs "tournaments-service"
            ;;
        matches)
            show_logs "matches-service"
            ;;
        auth)
            show_logs "auth-service"
            ;;
        teams)
            show_logs "teams-service"
            ;;
        notifications)
            show_logs "notifications-service"
            ;;
        postgres)
            show_logs "postgres"
            ;;
        mongodb)
            show_logs "mongodb"
            ;;
        redis)
            show_logs "redis"
            ;;
        rabbitmq)
            show_logs "rabbitmq"
            ;;
        follow)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ Error: Debes especificar un servicio${NC}"
                echo -e "Ejemplo: ./view-logs.sh follow tournaments"
                exit 1
            fi
            follow_logs "$2"
            ;;
        errors)
            show_errors
            ;;
        stats)
            show_stats
            ;;
        clean)
            clean_logs
            ;;
        *)
            echo -e "${RED}❌ Opción no reconocida: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar script
main "$@"
