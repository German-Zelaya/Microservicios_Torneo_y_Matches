#!/bin/bash

# Script para exportar logs a archivos
# Uso: ./export-logs.sh [servicio] [output_dir]

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Directorio de salida por defecto
OUTPUT_DIR="${2:-./logs-export}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"

# Función para exportar logs de un servicio
export_service_logs() {
    local service=$1
    local filename="${OUTPUT_DIR}/${service}_${TIMESTAMP}.log"
    
    echo -e "${BLUE}📦 Exportando logs de: ${YELLOW}$service${NC}"
    
    if docker-compose ps | grep -q "$service"; then
        docker-compose logs --no-color --timestamps "$service" > "$filename" 2>/dev/null
        
        local size=$(du -h "$filename" | cut -f1)
        echo -e "${GREEN}✅ Exportado: $filename ($size)${NC}"
    else
        echo -e "${RED}❌ Servicio no encontrado o no está corriendo: $service${NC}"
    fi
}

# Función para exportar todos los logs
export_all_logs() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📦 Exportando TODOS los logs${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Exportar logs de cada servicio
    for service in tournaments-service matches-service auth-service teams-service notifications-service postgres mongodb redis rabbitmq; do
        export_service_logs "$service"
    done
    
    # Crear archivo combinado
    local combined_file="${OUTPUT_DIR}/all-services_${TIMESTAMP}.log"
    echo -e "\n${BLUE}📦 Creando archivo combinado...${NC}"
    docker-compose logs --no-color --timestamps > "$combined_file" 2>/dev/null
    local size=$(du -h "$combined_file" | cut -f1)
    echo -e "${GREEN}✅ Archivo combinado: $combined_file ($size)${NC}"
    
    # Crear reporte de resumen
    create_summary_report
}

# Función para crear reporte de resumen
create_summary_report() {
    local report_file="${OUTPUT_DIR}/summary_${TIMESTAMP}.txt"
    
    echo -e "\n${BLUE}📊 Creando reporte de resumen...${NC}"
    
    {
        echo "═══════════════════════════════════════════════════════════"
        echo "  REPORTE DE LOGS - $(date)"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        echo "SERVICIOS ACTIVOS:"
        docker-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null
        echo ""
        echo "ESTADÍSTICAS DE LOGS (últimas 1000 líneas):"
        docker-compose logs --tail=1000 2>/dev/null | grep -io "error\|warning\|info\|debug" | sort | uniq -c | sort -rn
        echo ""
        echo "ERRORES RECIENTES:"
        docker-compose logs --tail=500 2>/dev/null | grep -iE "error|exception|failed|fatal" | tail -20
        echo ""
        echo "ARCHIVOS EXPORTADOS:"
        ls -lh "$OUTPUT_DIR"/*_${TIMESTAMP}.log 2>/dev/null
        echo ""
        echo "═══════════════════════════════════════════════════════════"
    } > "$report_file"
    
    echo -e "${GREEN}✅ Reporte creado: $report_file${NC}"
}

# Función principal
main() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Error: Docker no está corriendo${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📋 EXPORTADOR DE LOGS CENTRALIZADOS${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if [ -z "$1" ]; then
        export_all_logs
    else
        export_service_logs "$1"
    fi
    
    echo ""
    echo -e "${GREEN}✨ Exportación completada${NC}"
    echo -e "${YELLOW}📁 Directorio de salida: $OUTPUT_DIR${NC}"
    echo ""
}

main "$@"
