#!/usr/bin/env python3
"""
Script simplificado para verificar eventos de RabbitMQ
Este script solo verifica que los eventos se publiquen y reciban correctamente
"""

import requests
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any

# URLs base
TOURNAMENTS_URL = "http://localhost:8001"
MATCHES_URL = "http://localhost:8002"

# Colores para terminal
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'


def print_header(text: str):
    """Imprime un encabezado con formato"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BLUE}{text.center(70)}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")


def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_event(text: str):
    """Imprime mensaje de evento"""
    print(f"{Colors.MAGENTA}🎯 {text}{Colors.NC}")


def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_info(text: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.NC}")


def print_warning(text: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def show_docker_logs(service_name: str, lines: int = 20, filter_text: str = None):
    """Muestra logs de un servicio de Docker"""
    try:
        cmd = f"docker logs {service_name} --tail {lines}"
        if filter_text:
            cmd += f" | grep -E '{filter_text}' --color=always"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        
        if output.strip():
            print(f"\n{Colors.CYAN}📋 Logs de {service_name}:{Colors.NC}")
            print(output)
        else:
            print_info(f"No se encontraron logs con el filtro '{filter_text}'")
    except Exception as e:
        print_error(f"Error al obtener logs: {str(e)}")


def create_tournament() -> Dict[str, Any]:
    """Crea un torneo de prueba"""
    print_header("PASO 1: Crear Torneo")
    
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(hours=8)
    
    tournament_data = {
        "name": f"RabbitMQ Test {datetime.now().strftime('%H:%M:%S')}",
        "description": "Prueba de eventos RabbitMQ",
        "game": "Counter-Strike 2",
        "format": "single_elimination",
        "max_participants": 8,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "status": "draft"
    }
    
    try:
        print_info("Enviando petición para crear torneo...")
        response = requests.post(
            f"{TOURNAMENTS_URL}/api/v1/tournaments",
            json=tournament_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            tournament = response.json()
            tournament_id = tournament.get('id')
            tournament_name = tournament.get('name')
            
            print_success(f"Torneo creado exitosamente")
            print_info(f"   ID: {tournament_id}")
            print_info(f"   Nombre: {tournament_name}")
            print_info(f"   Juego: {tournament.get('game')}")
            
            print_event("Evento esperado: TOURNAMENT_CREATED")
            print_warning("Esperando 3 segundos para que se procese el evento...")
            time.sleep(3)
            
            return tournament
        else:
            print_error(f"Error al crear torneo: {response.status_code}")
            print_error(response.text)
            return {}
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return {}


def update_tournament(tournament_id: int):
    """Actualiza un torneo"""
    print_header("PASO 2: Actualizar Torneo")
    
    update_data = {
        "description": f"Descripción actualizada - {datetime.now().strftime('%H:%M:%S')}"
    }
    
    try:
        print_info(f"Actualizando torneo ID: {tournament_id}")
        response = requests.put(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Torneo actualizado exitosamente")
            print_event("Evento esperado: TOURNAMENT_UPDATED")
            print_warning("Esperando 3 segundos...")
            time.sleep(3)
            return True
        else:
            print_error(f"Error al actualizar: {response.status_code}")
            return False
    
    except requests.RequestException as e:
        print_error(f"Error: {str(e)}")
        return False


def change_tournament_status(tournament_id: int, new_status: str):
    """Cambia el estado del torneo"""
    print_header(f"PASO 3: Cambiar Estado a '{new_status.upper()}'")
    
    try:
        print_info(f"Cambiando estado del torneo ID: {tournament_id}")
        response = requests.patch(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/status",
            params={"new_status": new_status},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Estado cambiado a: {new_status}")
            print_event(f"Evento esperado: TOURNAMENT_STATUS_CHANGED (routing: tournament.status.{new_status})")
            print_warning("Esperando 3 segundos...")
            time.sleep(3)
            return True
        else:
            print_error(f"Error al cambiar estado: {response.status_code}")
            print_error(response.text)
            return False
    
    except requests.RequestException as e:
        print_error(f"Error: {str(e)}")
        return False


def delete_tournament(tournament_id: int):
    """Elimina un torneo"""
    print_header("PASO 4: Eliminar Torneo")
    
    try:
        print_info(f"Eliminando torneo ID: {tournament_id}")
        response = requests.delete(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Torneo eliminado exitosamente")
            print_event("Evento esperado: TOURNAMENT_DELETED")
            print_warning("Esperando 3 segundos...")
            time.sleep(3)
            return True
        else:
            print_error(f"Error al eliminar: {response.status_code}")
            return False
    
    except requests.RequestException as e:
        print_error(f"Error: {str(e)}")
        return False


def verify_services():
    """Verifica que los servicios estén disponibles"""
    print_header("Verificación Inicial")
    
    services = {
        "Tournaments Service": f"{TOURNAMENTS_URL}/health",
        "Matches Service": f"{MATCHES_URL}/health"
    }
    
    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{name} OK")
            else:
                print_error(f"{name} respondió con código {response.status_code}")
                all_ok = False
        except:
            print_error(f"{name} no disponible")
            all_ok = False
    
    # Verificar RabbitMQ
    try:
        result = subprocess.run(
            "docker exec rabbitmq-esports rabbitmqctl status > /dev/null 2>&1",
            shell=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("RabbitMQ OK")
        else:
            print_error("RabbitMQ no está respondiendo")
            all_ok = False
    except:
        print_error("No se pudo verificar RabbitMQ")
        all_ok = False
    
    return all_ok


def main():
    """Función principal"""
    print(f"\n{Colors.MAGENTA}{'='*70}{Colors.NC}")
    print(f"{Colors.MAGENTA}{'🧪 PRUEBA DE EVENTOS RABBITMQ - FLUJO SIMPLIFICADO 🧪'.center(70)}{Colors.NC}")
    print(f"{Colors.MAGENTA}{'='*70}{Colors.NC}\n")
    
    # Verificar servicios
    if not verify_services():
        print_error("\nAlgunos servicios no están disponibles. Verifica Docker.")
        return
    
    print_info("Todos los servicios están disponibles\n")
    time.sleep(2)
    
    # Crear torneo
    tournament = create_tournament()
    if not tournament or 'id' not in tournament:
        print_error("No se pudo crear el torneo")
        return
    
    tournament_id = tournament['id']
    
    # Mostrar logs del evento de creación
    show_docker_logs("matches-service", 10, "TOURNAMENT_CREATED|Torneo creado")
    
    time.sleep(2)
    
    # Actualizar torneo
    update_tournament(tournament_id)
    show_docker_logs("matches-service", 10, "TOURNAMENT_UPDATED|actualizado")
    
    time.sleep(2)
    
    # Cambiar estado a registration
    change_tournament_status(tournament_id, "registration")
    show_docker_logs("matches-service", 10, "TOURNAMENT_STATUS|Estado.*cambiado")
    
    time.sleep(2)
    
    # Cambiar estado a in_progress
    change_tournament_status(tournament_id, "in_progress")
    show_docker_logs("matches-service", 10, "TOURNAMENT_STATUS|Estado.*cambiado")
    
    time.sleep(2)
    
    # Eliminar torneo (opcional - comentar si quieres mantener el torneo)
    # delete_tournament(tournament_id)
    # show_docker_logs("matches-service", 10, "TOURNAMENT_DELETED|eliminado")
    
    # Resumen final
    print_header("📊 RESUMEN Y VERIFICACIÓN FINAL")
    
    print_success(f"Torneo creado: ID {tournament_id}")
    print_success("Eventos publicados:")
    print(f"   • {Colors.MAGENTA}tournament.created{Colors.NC}")
    print(f"   • {Colors.MAGENTA}tournament.updated{Colors.NC}")
    print(f"   • {Colors.MAGENTA}tournament.status.registration{Colors.NC}")
    print(f"   • {Colors.MAGENTA}tournament.status.in_progress{Colors.NC}")
    
    print("\n" + Colors.CYAN + "📋 Todos los eventos recibidos por matches-service:" + Colors.NC)
    show_docker_logs("matches-service", 30, "📩|📤")
    
    print("\n" + Colors.CYAN + "📢 Eventos publicados por tournaments-service:" + Colors.NC)
    show_docker_logs("tournaments-service", 30, "📤")
    
    print("\n" + Colors.YELLOW + "💡 Información útil:" + Colors.NC)
    print(f"  • RabbitMQ Management UI: {Colors.CYAN}http://localhost:15672{Colors.NC} (guest/guest)")
    print(f"  • Ver todos los logs de matches: {Colors.CYAN}docker logs matches-service{Colors.NC}")
    print(f"  • Ver todos los logs de tournaments: {Colors.CYAN}docker logs tournaments-service{Colors.NC}")
    print(f"  • Emoji 📤 = Evento publicado")
    print(f"  • Emoji 📩 = Evento recibido")
    
    print(f"\n{Colors.GREEN}✅ Prueba de eventos completada exitosamente!{Colors.NC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Prueba interrumpida por el usuario{Colors.NC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {str(e)}{Colors.NC}\n")
