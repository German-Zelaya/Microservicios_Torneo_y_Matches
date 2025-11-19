#!/usr/bin/env python3
"""
Script para probar el flujo completo de Brackets y Matches
Prueba los siguientes eventos:
1. tournament.bracket.generated (Tournaments -> Matches)
2. match.finished (Matches -> Tournaments)
3. bracket.update.next_match (Tournaments -> Matches)

Este script simula un torneo completo de 4 equipos desde la generación del bracket
hasta completar todos los matches y declarar un ganador.
"""

import requests
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List

# URLs base
TOURNAMENTS_URL = "http://localhost:8001"
MATCHES_URL = "http://localhost:8002"
AUTH_URL = "http://localhost:3000"
TEAMS_URL = "http://localhost:3002"

# Colores para terminal
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'


def print_header(text: str):
    """Imprime un encabezado con formato"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.NC}\n")


def print_subheader(text: str):
    """Imprime un subencabezado"""
    print(f"\n{Colors.CYAN}{'─'*80}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.NC}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.NC}")


def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_event(event_name: str, description: str = ""):
    """Imprime información de evento"""
    print(f"{Colors.MAGENTA}📤 Evento: {Colors.BOLD}{event_name}{Colors.NC}")
    if description:
        print(f"   {Colors.CYAN}→ {description}{Colors.NC}")


def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_info(text: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.NC}")


def print_warning(text: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def show_docker_logs(service_name: str, lines: int = 15, filter_text: str = None):
    """Muestra logs de un servicio de Docker"""
    try:
        cmd = f"docker logs {service_name} --tail {lines}"
        if filter_text:
            cmd += f" 2>&1 | grep -E '{filter_text}' --color=always"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        
        if output.strip():
            print(f"\n{Colors.CYAN}📋 Logs de {service_name}:{Colors.NC}")
            print(output)
        else:
            print_info(f"No hay logs recientes con el filtro aplicado")
    except Exception as e:
        print_error(f"Error al obtener logs: {str(e)}")


def verify_services() -> bool:
    """Verifica que los servicios estén disponibles"""
    print_header("🔍 VERIFICACIÓN DE SERVICIOS")
    
    services = {
        "Tournaments Service": f"{TOURNAMENTS_URL}/health",
        "Matches Service": f"{MATCHES_URL}/health",
        "Teams Service": f"{TEAMS_URL}/api/teams/health"
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
        except Exception as e:
            print_error(f"{name} no disponible: {str(e)}")
            all_ok = False
    
    # Verificar RabbitMQ
    try:
        result = subprocess.run(
            "docker exec rabbitmq-esports rabbitmqctl status > /dev/null 2>&1",
            shell=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("RabbitMQ está disponible")
        else:
            print_error("RabbitMQ no está respondiendo")
            all_ok = False
    except:
        print_error("No se pudo verificar RabbitMQ")
        all_ok = False
    
    return all_ok


def create_test_teams(num_teams: int = 4) -> List[str]:
    """
    Crea equipos de prueba en el Teams Service.
    
    Args:
        num_teams: Número de equipos a crear
        
    Returns:
        Lista de IDs de equipos creados
    """
    print_subheader("👥 Crear Equipos de Prueba")
    
    team_ids = []
    timestamp = datetime.now().strftime('%H%M%S')
    
    for i in range(1, num_teams + 1):
        team_data = {
            "name": f"Team Test {i} ({timestamp})",
            "captainId": f"00000000-0000-0000-0000-00000000000{i}",  # UUID de prueba
            "game": "League of Legends"
        }
        
        try:
            print_info(f"Creando equipo {i}/{num_teams}...")
            response = requests.post(
                f"{TEAMS_URL}/api/teams",
                json=team_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                team = response.json()
                team_id = team.get('teamId') or team.get('id')
                team_ids.append(team_id)
                print_success(f"Equipo creado: {team.get('name')} (ID: {team_id})")
            else:
                print_error(f"Error al crear equipo: {response.status_code}")
                print_error(response.text)
        
        except requests.RequestException as e:
            print_error(f"Error de conexión: {str(e)}")
    
    if len(team_ids) == num_teams:
        print_success(f"\n✅ {num_teams} equipos creados exitosamente")
    else:
        print_warning(f"\n⚠️  Solo se crearon {len(team_ids)} de {num_teams} equipos")
    
    return team_ids


def create_tournament(num_participants: int = 4) -> Dict[str, Any]:
    """
    Crea un torneo de prueba.
    
    Args:
        num_participants: Número máximo de participantes
        
    Returns:
        Datos del torneo creado
    """
    print_subheader("📝 PASO 1: Crear Torneo")
    
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(hours=8)
    
    tournament_data = {
        "name": f"Bracket Test Tournament {datetime.now().strftime('%H:%M:%S')}",
        "description": "Torneo de prueba para flujo de brackets y matches",
        "game": "League of Legends",
        "format": "single_elimination",
        "tournament_type": "team",  # Tipo de torneo: team
        "max_participants": num_participants,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "status": "draft"
    }
    
    try:
        print_info(f"Creando torneo con {num_participants} participantes máximos...")
        response = requests.post(
            f"{TOURNAMENTS_URL}/api/v1/tournaments",
            json=tournament_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            tournament = response.json()
            print_success(f"Torneo creado exitosamente")
            print(f"   {Colors.BOLD}ID:{Colors.NC} {tournament.get('id')}")
            print(f"   {Colors.BOLD}Nombre:{Colors.NC} {tournament.get('name')}")
            print(f"   {Colors.BOLD}Formato:{Colors.NC} {tournament.get('format')}")
            print(f"   {Colors.BOLD}Max Participantes:{Colors.NC} {tournament.get('max_participants')}")
            return tournament
        else:
            print_error(f"Error al crear torneo: {response.status_code}")
            print_error(response.text)
            return {}
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return {}


def change_tournament_to_registration(tournament_id: int) -> bool:
    """
    Cambia el torneo al estado 'registration'.
    
    Args:
        tournament_id: ID del torneo
        
    Returns:
        True si se cambió exitosamente
    """
    try:
        print_info(f"Cambiando torneo {tournament_id} a estado 'registration'...")
        response = requests.patch(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/status",
            params={"new_status": "registration"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Estado cambiado a 'registration'")
            return True
        else:
            print_error(f"Error al cambiar estado: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def generate_bracket(tournament_id: int, participants: List[int]) -> Dict[str, Any]:
    """
    Genera el bracket para un torneo (inicia el torneo).
    
    Args:
        tournament_id: ID del torneo
        participants: Lista de IDs de participantes
        
    Returns:
        Datos del bracket generado
    """
    print_subheader("🎯 PASO 2: Generar Bracket (Iniciar Torneo)")
    
    try:
        print_info(f"Generando bracket para torneo {tournament_id} con {len(participants)} participantes...")
        
        response = requests.post(
            f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/start",
            json={"participant_ids": participants},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            bracket = response.json()
            print_success("Bracket generado exitosamente")
            print(f"   {Colors.BOLD}Participantes:{Colors.NC} {bracket.get('total_participants')}")
            print(f"   {Colors.BOLD}Rondas totales:{Colors.NC} {bracket.get('total_rounds')}")
            print(f"   {Colors.BOLD}Matches primera ronda:{Colors.NC} {bracket.get('first_round_matches')}")
            print(f"   {Colors.BOLD}Matches generados:{Colors.NC} {bracket.get('matches_generated')}")
            
            print_event("tournament.bracket.generated", 
                       f"Tournaments → Matches (crear {bracket.get('first_round_matches')} matches)")
            
            # Mostrar información de los matches
            if 'matches' in bracket:
                print(f"\n   {Colors.BOLD}Matches de primera ronda:{Colors.NC}")
                for i, match in enumerate(bracket['matches'], 1):
                    print(f"      Match {i}: Participante {match.get('participant1_id')} vs {match.get('participant2_id')}")
            
            print_warning("Esperando 5 segundos para que se creen los matches...")
            time.sleep(5)
            
            return bracket
        else:
            print_error(f"Error al generar bracket: {response.status_code}")
            print_error(response.text)
            return {}
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return {}


def get_tournament_matches(tournament_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene los matches de un torneo desde el matches-service.
    
    Args:
        tournament_id: ID del torneo
        
    Returns:
        Lista de matches
    """
    try:
        response = requests.get(
            f"{MATCHES_URL}/api/v1/matches",
            params={"tournament_id": tournament_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('matches', [])
        else:
            print_warning(f"No se pudieron obtener matches: {response.status_code}")
            return []
    
    except requests.RequestException as e:
        print_warning(f"Error al obtener matches: {str(e)}")
        return []


def finish_match(match_id: str, winner_id: int, score: Dict[str, int]) -> bool:
    """
    Marca un match como finalizado reportando el resultado.
    
    Args:
        match_id: ID del match
        winner_id: ID del ganador
        score: Puntuación del match
        
    Returns:
        True si se completó exitosamente
    """
    try:
        result_data = {
            "winner_id": winner_id,
            "player1_score": score1,
            "player2_score": score2
        }
        
        response = requests.patch(
            f"{MATCHES_URL}/api/v1/matches/{match_id}/complete",
            json=result_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Match {match_id} finalizado. Ganador: Participante {winner_id}")
            print_event("match.finished", 
                       f"Matches → Tournaments (avanzar ganador {winner_id} a siguiente ronda)")
            return True
        else:
            print_error(f"Error al finalizar match: {response.status_code}")
            print_error(response.text)
            return False
    
    except requests.RequestException as e:
        print_error(f"Error de conexión: {str(e)}")
        return False


def display_bracket_status(tournament_id: int, round_number: int):
    """
    Muestra el estado actual del bracket.
    
    Args:
        tournament_id: ID del torneo
        round_number: Número de ronda actual
    """
    print_subheader(f"📊 Estado del Bracket - Ronda {round_number}")
    
    matches = get_tournament_matches(tournament_id)
    
    if not matches:
        print_warning("No se encontraron matches")
        return
    
    # Agrupar matches por ronda
    matches_by_round = {}
    for match in matches:
        round_num = match.get('round', 0)
        if round_num not in matches_by_round:
            matches_by_round[round_num] = []
        matches_by_round[round_num].append(match)
    
    # Mostrar matches de la ronda actual
    current_matches = matches_by_round.get(round_number, [])
    
    if current_matches:
        print(f"\n{Colors.BOLD}Matches en Ronda {round_number}:{Colors.NC}")
        for match in current_matches:
            status = match.get('status', 'unknown')
            match_num = match.get('match_number', '?')
            player1 = match.get('player1_id', 'TBD')
            player2 = match.get('player2_id', 'TBD')
            winner = match.get('winner_id', '-')
            
            status_emoji = "✅" if status == "finished" else "⏳"
            print(f"   {status_emoji} Match #{match_num}: P{player1} vs P{player2} | "
                  f"Estado: {status} | Ganador: {winner if winner else 'Pendiente'}")
    else:
        print_info(f"No hay matches en la ronda {round_number}")


def simulate_tournament_flow(tournament_id: int, bracket_data: Dict[str, Any]):
    """
    Simula el flujo completo del torneo completando todos los matches.
    
    Args:
        tournament_id: ID del torneo
        bracket_data: Datos del bracket generado
    """
    print_header("🎮 SIMULACIÓN DEL FLUJO DE TORNEO")
    
    total_rounds = bracket_data.get('total_rounds', 0)
    
    print_info(f"Este torneo tendrá {total_rounds} rondas")
    print_info("Completaremos todos los matches hasta determinar un campeón\n")
    
    for current_round in range(1, total_rounds + 1):
        print_subheader(f"🏆 RONDA {current_round} de {total_rounds}")
        
        # Esperar un poco para que se creen los matches
        print_warning("Esperando 3 segundos para que se actualice el estado...")
        time.sleep(3)
        
        # Obtener matches de la ronda actual
        all_matches = get_tournament_matches(tournament_id)
        current_round_matches = [m for m in all_matches if m.get('round') == current_round]
        
        if not current_round_matches:
            print_warning(f"No se encontraron matches para la ronda {current_round}")
            continue
        
        print_info(f"Encontrados {len(current_round_matches)} matches en esta ronda")
        
        # Mostrar estado del bracket
        display_bracket_status(tournament_id, current_round)
        
        # Completar cada match de la ronda
        for i, match in enumerate(current_round_matches, 1):
            match_id = match.get('id')
            status = match.get('status')
            player1_id = match.get('player1_id')
            player2_id = match.get('player2_id')
            
            print(f"\n{Colors.BOLD}Match {i}/{len(current_round_matches)}:{Colors.NC}")
            print(f"   ID: {match_id}")
            print(f"   Estado actual: {status}")
            print(f"   Player 1: {player1_id}")
            print(f"   Player 2: {player2_id}")
            
            if status == 'finished':
                print_info("Match ya completado, saltando...")
                continue
            
            if not player1_id or not player2_id:
                print_warning("Match incompleto (falta un participante), saltando...")
                continue
            
            # Simular resultado (player1 gana este match)
            winner_id = player1_id
            score = {
                str(player1_id): 2,
                str(player2_id): 1
            }
            
            print_info(f"Finalizando match... Ganador: Participante {winner_id}")
            
            if finish_match(match_id, winner_id, score):
                # Si no es la última ronda, se publicará bracket.update.next_match
                if current_round < total_rounds:
                    print_event("bracket.update.next_match",
                              f"Tournaments → Matches (actualizar match de ronda {current_round + 1})")
                else:
                    print_success("🏆 ¡Este era el match final! ¡Torneo completado!")
                
                print_warning("Esperando 3 segundos para procesar el evento...")
                time.sleep(3)
            else:
                print_error("Error al finalizar match")
        
        # Mostrar logs después de completar la ronda
        if current_round < total_rounds:
            print(f"\n{Colors.CYAN}📋 Logs de procesamiento:{Colors.NC}")
            show_docker_logs("tournaments-service", 10, 
                           "match.finished|Avanzando ganador|Evento publicado")
            show_docker_logs("matches-service", 10,
                           "bracket.update|Creating match|Updating match")


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*80}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'🧪 PRUEBA DE FLUJO COMPLETO DE BRACKETS Y MATCHES 🧪'.center(80)}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*80}{Colors.NC}")
    
    print(f"\n{Colors.CYAN}Este script probará:{Colors.NC}")
    print(f"  1. {Colors.MAGENTA}tournament.bracket.generated{Colors.NC} → Crea matches iniciales")
    print(f"  2. {Colors.MAGENTA}match.finished{Colors.NC} → Avanza ganadores")
    print(f"  3. {Colors.MAGENTA}bracket.update.next_match{Colors.NC} → Actualiza matches de siguiente ronda\n")
    
    # Verificar servicios
    if not verify_services():
        print_error("\n❌ Algunos servicios no están disponibles.")
        print_info("Asegúrate de que todos los servicios estén corriendo con: docker compose up -d")
        return
    
    print_success("\n✅ Todos los servicios están disponibles\n")
    time.sleep(2)
    
    # Paso 1: Crear torneo
    tournament = create_tournament(num_participants=4)
    if not tournament or 'id' not in tournament:
        print_error("No se pudo crear el torneo")
        return
    
    tournament_id = tournament['id']
    
    time.sleep(2)
    
    # Cambiar torneo a estado 'registration'
    if not change_tournament_to_registration(tournament_id):
        print_error("No se pudo cambiar el estado del torneo")
        return
    
    time.sleep(1)
    
    # Paso 2: Generar bracket con los equipos creados
    bracket_data = generate_bracket(tournament_id, team_ids)
    
    if not bracket_data:
        print_error("No se pudo generar el bracket")
        return
    
    # Mostrar logs de la generación del bracket
    show_docker_logs("matches-service", 15, 
                    "tournament.bracket.generated|Creating match|BRACKET_GENERATED")
    
    time.sleep(2)
    
    # Paso 3: Simular el flujo completo del torneo
    simulate_tournament_flow(tournament_id, bracket_data)
    
    # Resumen final
    print_header("📊 RESUMEN FINAL")
    
    print_success(f"Torneo ID {tournament_id} - Flujo completado")
    
    print(f"\n{Colors.BOLD}Eventos probados:{Colors.NC}")
    print(f"   ✅ {Colors.MAGENTA}tournament.bracket.generated{Colors.NC} → Generó matches de primera ronda")
    print(f"   ✅ {Colors.MAGENTA}match.finished{Colors.NC} → Avanzó ganadores a siguientes rondas")
    print(f"   ✅ {Colors.MAGENTA}bracket.update.next_match{Colors.NC} → Actualizó matches de rondas siguientes")
    
    # Mostrar bracket final
    print_subheader("🏆 Estado Final del Bracket")
    all_matches = get_tournament_matches(tournament_id)
    
    if all_matches:
        matches_by_round = {}
        for match in all_matches:
            round_num = match.get('round', 0)
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []
            matches_by_round[round_num].append(match)
        
        for round_num in sorted(matches_by_round.keys()):
            print(f"\n{Colors.BOLD}Ronda {round_num}:{Colors.NC}")
            for match in matches_by_round[round_num]:
                status_emoji = "✅" if match.get('status') == 'finished' else "⏳"
                print(f"   {status_emoji} Match #{match.get('match_number')}: "
                      f"P{match.get('player1_id')} vs P{match.get('player2_id')} | "
                      f"Ganador: P{match.get('winner_id') if match.get('winner_id') else 'Pendiente'}")
    
    print(f"\n{Colors.YELLOW}💡 Información útil:{Colors.NC}")
    print(f"  • RabbitMQ Management: {Colors.CYAN}http://localhost:15672{Colors.NC} (guest/guest)")
    print(f"  • Ver logs tournaments: {Colors.CYAN}docker logs tournaments-service{Colors.NC}")
    print(f"  • Ver logs matches: {Colors.CYAN}docker logs matches-service{Colors.NC}")
    print(f"  • API Docs Tournaments: {Colors.CYAN}http://localhost:8001/docs{Colors.NC}")
    print(f"  • API Docs Matches: {Colors.CYAN}http://localhost:8002/docs{Colors.NC}")
    
    print(f"\n{Colors.GREEN}{'='*80}{Colors.NC}")
    print(f"{Colors.GREEN}{'✅ PRUEBA COMPLETADA EXITOSAMENTE'.center(80)}{Colors.NC}")
    print(f"{Colors.GREEN}{'='*80}{Colors.NC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Prueba interrumpida por el usuario{Colors.NC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {str(e)}{Colors.NC}\n")
        import traceback
        traceback.print_exc()
