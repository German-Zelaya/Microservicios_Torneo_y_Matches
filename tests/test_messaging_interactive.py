#!/usr/bin/env python3
"""
Script interactivo para probar eventos de RabbitMQ entre servicios
"""

import requests
import json
import time
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
    NC = '\033[0m'  # No Color


def print_header(text: str):
    """Imprime un encabezado con formato"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}{text.center(60)}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")


def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_info(text: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.NC}")


def print_warning(text: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def check_services() -> bool:
    """Verifica que todos los servicios estén disponibles"""
    print_header("Verificando Servicios")
    
    services = {
        "Tournaments Service": f"{TOURNAMENTS_URL}/health",
        "Matches Service": f"{MATCHES_URL}/health"
    }
    
    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{name} está disponible")
            else:
                print_error(f"{name} respondió con código {response.status_code}")
                all_ok = False
        except requests.RequestException as e:
            print_error(f"{name} no está disponible: {str(e)}")
            all_ok = False
    
    return all_ok


def create_tournament() -> Dict[str, Any]:
    """Crea un torneo de prueba"""
    print_header("Creando Torneo")
    
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(hours=8)
    
    tournament_data = {
        "name": f"Test Tournament {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "Torneo de prueba para eventos RabbitMQ",
        "game": "League of Legends",
        "format": "single_elimination",
        "max_participants": 8,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{TOURNAMENTS_URL}/api/v1/tournaments",
            json=tournament_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            tournament = response.json()
            print_success(f"Torneo creado con ID: {tournament.get('id')}")
            print_info(f"Nombre: {tournament.get('name')}")
            print_warning("Revisa los logs de matches-service para ver el evento TOURNAMENT_CREATED")
            return tournament
        else:
            print_error(f"Error al crear torneo: {response.status_code}")
            print_error(response.text)
            return {}
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return {}


def add_participants(tournament_id: int, count: int = 8) -> list:
    """Prepara la lista de participantes"""
    print_header(f"Preparando {count} Participantes")
    
    # Generar UUIDs de prueba
    participants = []
    for i in range(1, count + 1):
        user_id = f"00000000-0000-0000-0000-{str(i).zfill(12)}"
        participants.append(user_id)
        print_info(f"Participante {i}: {user_id}")
    
    return participants


def start_tournament_with_bracket(tournament_id: int, participant_ids: list) -> bool:
    """Inicia el torneo y genera el bracket"""
    print_header("Cambiando estado a REGISTRATION")
    
    # Primero cambiar estado a REGISTRATION
    try:
        response = requests.patch(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/status",
            params={"new_status": "registration"}
        )
        
        if response.status_code == 200:
            print_success("Estado cambiado a REGISTRATION")
        else:
            print_error(f"Error al cambiar estado: {response.status_code}")
            print_error(response.text)
            return False
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return False
    
    time.sleep(2)
    
    # Ahora iniciar torneo con participantes
    print_header("Iniciando Torneo y Generando Bracket")
    
    try:
        response = requests.post(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/start",
            json={"participant_ids": participant_ids},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            bracket = response.json()
            print_success("Torneo iniciado y bracket generado correctamente")
            print_info(f"Total de rondas: {bracket.get('total_rounds', 'N/A')}")
            print_info(f"Total de matches: {bracket.get('total_matches', 'N/A')}")
            print_warning("⏳ Esperando 5 segundos para procesar evento BRACKET_GENERATED...")
            time.sleep(5)
            print_warning("Revisa los logs de matches-service para ver los matches creados")
            return True
        else:
            print_error(f"Error al iniciar torneo: {response.status_code}")
            print_error(response.text)
            return False
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return False


def list_matches(tournament_id: int) -> list:
    """Lista los matches del torneo"""
    print_header("Listando Matches Creados")
    
    try:
        response = requests.get(
            f"{MATCHES_URL}/api/matches",
            params={"tournament_id": tournament_id}
        )
        
        if response.status_code == 200:
            matches = response.json()
            
            if isinstance(matches, list):
                print_success(f"Total de matches encontrados: {len(matches)}")
                
                # Mostrar primeros 3 matches
                for i, match in enumerate(matches[:3], 1):
                    print_info(f"Match {i}:")
                    print(f"   ID: {match.get('id')}")
                    print(f"   Round: {match.get('round')}")
                    print(f"   Status: {match.get('status')}")
                    print(f"   Player 1: {match.get('player1_id', 'TBD')}")
                    print(f"   Player 2: {match.get('player2_id', 'TBD')}")
                
                if len(matches) > 3:
                    print_info(f"... y {len(matches) - 3} matches más")
                
                return matches
            else:
                print_error("Formato de respuesta inesperado")
                return []
        else:
            print_error(f"Error al obtener matches: {response.status_code}")
            return []
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return []


def complete_match(match_id: int) -> bool:
    """Completa un match reportando un resultado"""
    print_header(f"Completando Match {match_id}")
    
    # 1. Iniciar el match
    print_info("Paso 1: Iniciando match...")
    try:
        response = requests.patch(f"{MATCHES_URL}/api/matches/{match_id}/start")
        if response.status_code == 200:
            print_success("Match iniciado")
        else:
            print_error(f"Error al iniciar match: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return False
    
    time.sleep(2)
    
    # 2. Reportar resultado
    print_info("Paso 2: Reportando resultado...")
    result_data = {
        "player1_score": 16,
        "player2_score": 8
    }
    
    try:
        response = requests.post(
            f"{MATCHES_URL}/api/matches/{match_id}/result",
            json=result_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print_success("Resultado reportado: Player 1 gana 16-8")
            print_warning("⏳ Esperando 5 segundos para procesar evento MATCH_FINISHED...")
            time.sleep(5)
            print_warning("Revisa los logs de tournaments-service y matches-service")
            return True
        else:
            print_error(f"Error al reportar resultado: {response.status_code}")
            print_error(response.text)
            return False
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return False


def main():
    """Función principal"""
    print_header("🧪 PRUEBA DE EVENTOS RABBITMQ 🧪")
    
    # 1. Verificar servicios
    if not check_services():
        print_error("Algunos servicios no están disponibles. Verifica que Docker esté corriendo.")
        return
    
    time.sleep(2)
    
    # 2. Crear torneo
    tournament = create_tournament()
    if not tournament or 'id' not in tournament:
        print_error("No se pudo crear el torneo")
        return
    
    tournament_id = tournament['id']
    time.sleep(2)
    
    # 3. Preparar participantes
    participants = add_participants(8)
    
    time.sleep(2)
    
    # 4. Iniciar torneo y generar bracket
    if not start_tournament_with_bracket(tournament_id, participants):
        print_error("No se pudo iniciar el torneo y generar el bracket")
        return
    
    # 5. Listar matches
    matches = list_matches(tournament_id)
    if not matches:
        print_error("No se encontraron matches")
        return
    
    time.sleep(2)
    
    # 6. Completar primer match
    first_match = matches[0]
    if 'id' in first_match:
        complete_match(first_match['id'])
    
    # Resumen final
    print_header("📊 RESUMEN DE PRUEBAS")
    print_success(f"Torneo creado: ID {tournament_id}")
    print_success(f"Participantes: 8")
    print_success(f"Matches creados: {len(matches)}")
    if matches and 'id' in matches[0]:
        print_success(f"Match completado: {matches[0].get('id', 'N/A')}")
    
    print("\n" + Colors.CYAN + "💡 Consejos:" + Colors.NC)
    print("  1. Accede a RabbitMQ Management UI: http://localhost:15672 (guest/guest)")
    print("  2. Ver logs de tournaments: docker logs tournaments-service")
    print("  3. Ver logs de matches: docker logs matches-service")
    print("  4. Los eventos publicados aparecerán con emoji 📤")
    print("  5. Los eventos recibidos aparecerán con emoji 📩")
    
    print_success("\n✅ Prueba completada!\n")


if __name__ == "__main__":
    main()
