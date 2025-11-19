#!/usr/bin/env python3
"""
Dashboard de estado de eventos RabbitMQ
"""

import subprocess
import requests
import sys

# Colores
class C:
    G = '\033[0;32m'  # Green
    Y = '\033[1;33m'  # Yellow
    B = '\033[0;34m'  # Blue
    R = '\033[0;31m'  # Red
    C = '\033[0;36m'  # Cyan
    M = '\033[0;35m'  # Magenta
    W = '\033[1;37m'  # White
    N = '\033[0m'     # Reset


def print_header():
    print(f"\n{C.M}{'='*70}{C.N}")
    print(f"{C.M}{'🎯 ESTADO DE EVENTOS RABBITMQ'.center(70)}{C.N}")
    print(f"{C.M}{'='*70}{C.N}\n")


def check_docker_service(service_name):
    """Verifica si un servicio de Docker está corriendo"""
    try:
        result = subprocess.run(
            f"docker ps --filter 'name={service_name}' --format '{{{{.Status}}}}'",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        status = result.stdout.strip()
        return bool(status and "Up" in status), status
    except:
        return False, "Error"


def check_http_service(url):
    """Verifica si un servicio HTTP está respondiendo"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False


def get_rabbitmq_info():
    """Obtiene información de RabbitMQ"""
    try:
        # Obtener exchanges
        result_exchanges = subprocess.run(
            "docker exec rabbitmq-esports rabbitmqctl list_exchanges name type 2>/dev/null | grep tournaments",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Obtener queues
        result_queues = subprocess.run(
            "docker exec rabbitmq-esports rabbitmqctl list_queues name messages 2>/dev/null | grep matches",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {
            'exchange': result_exchanges.stdout.strip() if result_exchanges.returncode == 0 else None,
            'queue': result_queues.stdout.strip() if result_queues.returncode == 0 else None
        }
    except:
        return {'exchange': None, 'queue': None}


def count_events_in_logs(service_name, pattern):
    """Cuenta eventos en los logs"""
    try:
        result = subprocess.run(
            f"docker logs {service_name} 2>&1 | grep -c '{pattern}'",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        count = result.stdout.strip()
        return int(count) if count.isdigit() else 0
    except:
        return 0


def main():
    print_header()
    
    # Verificar servicios Docker
    print(f"{C.C}📦 ESTADO DE CONTENEDORES{C.N}")
    print(f"{'-'*70}")
    
    services = [
        ("tournaments-service", "Tournaments Service"),
        ("matches-service", "Matches Service"),
        ("rabbitmq-esports", "RabbitMQ")
    ]
    
    all_running = True
    for container, name in services:
        running, status = check_docker_service(container)
        icon = f"{C.G}✅" if running else f"{C.R}❌"
        print(f"{icon} {name:<25} {status[:40]}{C.N}")
        if not running:
            all_running = False
    
    print()
    
    # Verificar servicios HTTP
    print(f"{C.C}🌐 ESTADO DE SERVICIOS HTTP{C.N}")
    print(f"{'-'*70}")
    
    http_services = [
        ("http://localhost:8001/health", "Tournaments Service API"),
        ("http://localhost:8002/health", "Matches Service API"),
    ]
    
    for url, name in http_services:
        responding = check_http_service(url)
        icon = f"{C.G}✅" if responding else f"{C.R}❌"
        print(f"{icon} {name:<25} {url}{C.N}")
    
    print()
    
    # Info de RabbitMQ
    print(f"{C.C}🐰 CONFIGURACIÓN DE RABBITMQ{C.N}")
    print(f"{'-'*70}")
    
    rabbitmq_info = get_rabbitmq_info()
    
    if rabbitmq_info['exchange']:
        print(f"{C.G}✅ Exchange: {rabbitmq_info['exchange']}{C.N}")
    else:
        print(f"{C.Y}⚠️  Exchange: No se pudo obtener información{C.N}")
    
    if rabbitmq_info['queue']:
        print(f"{C.G}✅ Queue: {rabbitmq_info['queue']}{C.N}")
    else:
        print(f"{C.Y}⚠️  Queue: No se pudo obtener información{C.N}")
    
    print(f"{C.B}ℹ️  Management UI: http://localhost:15672 (guest/guest){C.N}")
    
    print()
    
    # Estadísticas de eventos
    print(f"{C.C}📊 ESTADÍSTICAS DE EVENTOS{C.N}")
    print(f"{'-'*70}")
    
    # Eventos publicados por tournaments
    published = count_events_in_logs("tournaments-service", "📤")
    print(f"{C.M}📤 Eventos publicados (Tournaments):{C.N} {published}")
    
    # Eventos recibidos por matches
    received = count_events_in_logs("matches-service", "📩")
    print(f"{C.C}📩 Eventos recibidos (Matches):{C.N} {received}")
    
    # Eventos específicos
    print(f"\n{C.W}Eventos por tipo:{C.N}")
    
    event_types = [
        ("TOURNAMENT_CREATED", "🆕 Torneos creados"),
        ("TOURNAMENT_UPDATED", "✏️  Torneos actualizados"),
        ("TOURNAMENT_STATUS_CHANGED", "🔄 Cambios de estado"),
        ("TOURNAMENT_DELETED", "🗑️  Torneos eliminados"),
    ]
    
    for event_type, label in event_types:
        count = count_events_in_logs("matches-service", event_type)
        color = C.G if count > 0 else C.Y
        print(f"  {color}{label:<30} {count}{C.N}")
    
    print()
    
    # Resumen final
    print(f"{C.M}{'='*70}{C.N}")
    if all_running:
        print(f"{C.G}✅ TODOS LOS SERVICIOS ESTÁN OPERATIVOS{C.N}")
        print(f"\n{C.C}💡 Para probar los eventos:{C.N}")
        print(f"   python3 test_events_simple.py")
        print(f"\n{C.C}💡 Para monitorear en vivo:{C.N}")
        print(f"   ./monitor-events.sh")
    else:
        print(f"{C.R}❌ ALGUNOS SERVICIOS NO ESTÁN DISPONIBLES{C.N}")
        print(f"\n{C.Y}💡 Inicia los servicios con:{C.N}")
        print(f"   docker-compose up -d")
    
    print(f"{C.M}{'='*70}{C.N}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C.Y}⚠️  Interrumpido por el usuario{C.N}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{C.R}❌ Error: {str(e)}{C.N}\n")
        sys.exit(1)
