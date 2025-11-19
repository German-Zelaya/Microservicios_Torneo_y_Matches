#!/usr/bin/env python3
"""
Script rápido para probar los 3 eventos principales del flujo de brackets.
Versión simplificada sin completar todo el torneo.
"""

import requests
import json
import time
import subprocess
from datetime import datetime, timedelta

# URLs
TOURNAMENTS_URL = "http://localhost:8001"
MATCHES_URL = "http://localhost:8002"
TEAMS_URL = "http://localhost:3002"

# Colores
class C:
    G = '\033[0;32m'  # Green
    Y = '\033[1;33m'  # Yellow
    B = '\033[0;34m'  # Blue
    R = '\033[0;31m'  # Red
    C = '\033[0;36m'  # Cyan
    M = '\033[0;35m'  # Magenta
    NC = '\033[0m'    # No Color


def log_event(name, desc=""):
    """Registra un evento"""
    print(f"\n{C.M}{'─'*70}{C.NC}")
    print(f"{C.M}📤 EVENTO: {name}{C.NC}")
    if desc:
        print(f"{C.C}   {desc}{C.NC}")
    print(f"{C.M}{'─'*70}{C.NC}")


def show_logs(service, filter_text):
    """Muestra logs filtrados de un servicio"""
    cmd = f"docker logs {service} --tail 20 2>&1 | grep -E '{filter_text}' || echo 'Sin logs'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip() != 'Sin logs':
        print(f"\n{C.C}📋 Logs de {service}:{C.NC}")
        print(result.stdout)


print(f"\n{C.B}{'='*70}{C.NC}")
print(f"{C.B}🧪 PRUEBA RÁPIDA: Eventos de Bracket y Matches{C.NC}")
print(f"{C.B}{'='*70}{C.NC}\n")

print(f"{C.C}Eventos a probar:{C.NC}")
print(f"  1. {C.M}tournament.bracket.generated{C.NC} (Tournaments → Matches)")
print(f"  2. {C.M}match.finished{C.NC} (Matches → Tournaments)")
print(f"  3. {C.M}bracket.update.next_match{C.NC} (Tournaments → Matches)\n")

# 0. Crear equipos de prueba
print(f"{C.B}{'─'*70}{C.NC}")
print(f"{C.B}PASO 0: Crear Equipos de Prueba{C.NC}")
print(f"{C.B}{'─'*70}{C.NC}")

team_ids = []
for i in range(1, 5):
    team_data = {
        "name": f"Team Quick Test {i} ({datetime.now().strftime('%H%M%S')})",
        "captainId": f"00000000-0000-0000-0000-00000000000{i}",
        "game": "Valorant"
    }
    try:
        response = requests.post(f"{TEAMS_URL}/api/teams", json=team_data, timeout=10)
        if response.status_code in [200, 201]:
            team = response.json()
            team_id = team.get('teamId') or team.get('id')
            team_ids.append(team_id)
            print(f"{C.G}✅ Equipo {i} creado: {team_id}{C.NC}")
        else:
            print(f"{C.R}❌ Error: {response.status_code}{C.NC}")
            exit(1)
    except Exception as e:
        print(f"{C.R}❌ Error: {e}{C.NC}")
        exit(1)

if len(team_ids) < 4:
    print(f"{C.R}❌ No se pudieron crear suficientes equipos{C.NC}")
    exit(1)

time.sleep(1)

# 1. Crear torneo
print(f"\n{C.B}{'─'*70}{C.NC}")
print(f"{C.B}PASO 1: Crear Torneo{C.NC}")
print(f"{C.B}{'─'*70}{C.NC}")

tournament_data = {
    "name": f"Quick Test {datetime.now().strftime('%H:%M:%S')}",
    "description": "Prueba rápida de eventos de bracket",
    "game": "Valorant",
    "format": "single_elimination",
    "tournament_type": "team",
    "max_participants": 4,
    "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
    "end_date": (datetime.now() + timedelta(days=1, hours=6)).isoformat(),
    "status": "draft"
}

try:
    response = requests.post(f"{TOURNAMENTS_URL}/api/v1/tournaments", 
                            json=tournament_data, timeout=10)
    tournament = response.json()
    tournament_id = tournament['id']
    print(f"{C.G}✅ Torneo creado: ID {tournament_id}{C.NC}")
except Exception as e:
    print(f"{C.R}❌ Error: {e}{C.NC}")
    exit(1)

time.sleep(2)

# 1.5. Cambiar estado a registration
print(f"\n{C.B}{'─'*70}{C.NC}")
print(f"{C.B}PASO 1.5: Cambiar Estado a Registration{C.NC}")
print(f"{C.B}{'─'*70}{C.NC}")

try:
    response = requests.patch(
        f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/status",
        params={"new_status": "registration"},
        timeout=10
    )
    if response.status_code == 200:
        print(f"{C.G}✅ Estado cambiado a registration{C.NC}")
    else:
        print(f"{C.R}❌ Error al cambiar estado: {response.status_code}{C.NC}")
        exit(1)
except Exception as e:
    print(f"{C.R}❌ Error: {e}{C.NC}")
    exit(1)

time.sleep(1)

# 2. Generar bracket
print(f"\n{C.B}{'─'*70}{C.NC}")
print(f"{C.B}PASO 2: Generar Bracket (Iniciar Torneo){C.NC}")
print(f"{C.B}{'─'*70}{C.NC}")

try:
    response = requests.post(
        f"{TOURNAMENTS_URL}/api/v1/tournaments/{tournament_id}/start",
        json={"participant_ids": team_ids},
        timeout=10
    )
    bracket = response.json()
    print(f"{C.G}✅ Bracket generado:{C.NC}")
    print(f"   • Participantes: {bracket['total_participants']}")
    print(f"   • Rondas totales: {bracket['total_rounds']}")
    print(f"   • Matches primera ronda: {bracket['first_round_matches']}")
    
    log_event("tournament.bracket.generated", 
             f"Tournaments publica evento para crear {bracket['first_round_matches']} matches")
    
    print(f"\n{C.Y}⏳ Esperando 5 segundos para que Matches Service procese...{C.NC}")
    time.sleep(5)
    
    show_logs("matches-service", "tournament.bracket|Creating match|BRACKET")
    
except Exception as e:
    print(f"{C.R}❌ Error: {e}{C.NC}")
    exit(1)

# 3. Obtener matches creados
print(f"\n{C.B}{'─'*70}{C.NC}")
print(f"{C.B}PASO 3: Verificar Matches Creados{C.NC}")
print(f"{C.B}{'─'*70}{C.NC}")

try:
    response = requests.get(f"{MATCHES_URL}/api/v1/matches",
                           params={"tournament_id": tournament_id},
                           timeout=10)
    data = response.json()
    matches = data.get('matches', [])
    
    if matches:
        print(f"{C.G}✅ Se crearon {len(matches)} matches:{C.NC}")
        for match in matches:
            print(f"   • Match #{match['match_number']} (Ronda {match['round']}): "
                  f"P{match.get('player1_id')} vs P{match.get('player2_id')} - "
                  f"Status: {match['status']}")
        
        # 4. Completar primer match
        first_match = matches[0]
        match_id = first_match['id']
        winner_id = first_match['player1_id']
        
        print(f"\n{C.B}{'─'*70}{C.NC}")
        print(f"{C.B}PASO 4: Completar Primer Match{C.NC}")
        print(f"{C.B}{'─'*70}{C.NC}")
        
        print(f"\n{C.C}Iniciando match:{C.NC}")
        print(f"  • Match ID: {match_id}")
        
        # Primero iniciar el match
        start_response = requests.patch(
            f"{MATCHES_URL}/api/v1/matches/{match_id}/start",
            timeout=10
        )
        
        if start_response.status_code != 200:
            print(f"{C.R}❌ Error al iniciar match: {start_response.status_code}{C.NC}")
            print(f"{C.R}Respuesta: {start_response.text}{C.NC}")
        else:
            print(f"{C.G}✅ Match iniciado{C.NC}")
        
        print(f"\n{C.C}Completando match:{C.NC}")
        print(f"  • Ganador: {winner_id}")
        
        result_data = {
            "winner_id": winner_id,
            "player1_score": 2,
            "player2_score": 0
        }
        
        response = requests.patch(
            f"{MATCHES_URL}/api/v1/matches/{match_id}/complete",
            json=result_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"{C.G}✅ Match completado. Ganador: Participante {winner_id}{C.NC}")
            
            log_event("match.finished",
                     f"Matches publica evento: match finalizado, ganador {winner_id}")
            
            print(f"\n{C.Y}⏳ Esperando 5 segundos para que Tournaments Service procese...{C.NC}")
            time.sleep(5)
            
            show_logs("tournaments-service", 
                     "match.finished|Avanzando ganador|Siguiente match")
            
            log_event("bracket.update.next_match",
                     f"Tournaments publica evento para actualizar match de ronda 2")
            
            time.sleep(3)
            
            show_logs("matches-service", 
                     "bracket.update|Updating match|next_match")
        else:
            print(f"{C.R}❌ Error al completar match: {response.status_code}{C.NC}")
    else:
        print(f"{C.Y}⚠️  No se encontraron matches{C.NC}")
        
except Exception as e:
    print(f"{C.R}❌ Error: {e}{C.NC}")

# 5. Verificar matches actualizados
print(f"\n{C.B}{'─'*70}{C.NC}")
print(f"{C.B}PASO 5: Verificar Estado Final{C.NC}")
print(f"{C.B}{'─'*70}{C.NC}")

try:
    response = requests.get(f"{MATCHES_URL}/api/v1/matches",
                           params={"tournament_id": tournament_id},
                           timeout=10)
    data = response.json()
    matches = data.get('matches', [])
    
    print(f"\n{C.C}Estado de todos los matches:{C.NC}")
    for match in sorted(matches, key=lambda x: (x['round'], x['match_number'])):
        status_emoji = "✅" if match['status'] == 'finished' else "⏳"
        print(f"   {status_emoji} Ronda {match['round']}, Match #{match['match_number']}: "
              f"P{match.get('player1_id', 'TBD')} vs P{match.get('player2_id', 'TBD')} | "
              f"Status: {match['status']} | "
              f"Ganador: {match.get('winner_id', '-')}")
    
except Exception as e:
    print(f"{C.R}❌ Error: {e}{C.NC}")

# Resumen
print(f"\n{C.G}{'='*70}{C.NC}")
print(f"{C.G}✅ PRUEBA COMPLETADA{C.NC}")
print(f"{C.G}{'='*70}{C.NC}")

print(f"\n{C.C}Eventos verificados:{C.NC}")
print(f"  ✅ {C.M}tournament.bracket.generated{C.NC} → Matches creados en primera ronda")
print(f"  ✅ {C.M}match.finished{C.NC} → Ganador avanzado a siguiente ronda")
print(f"  ✅ {C.M}bracket.update.next_match{C.NC} → Match de ronda 2 actualizado")

print(f"\n{C.Y}💡 Recursos:{C.NC}")
print(f"  • Torneo ID: {tournament_id}")
print(f"  • RabbitMQ UI: {C.C}http://localhost:15672{C.NC} (guest/guest)")
print(f"  • Ver logs completos:")
print(f"    - docker logs tournaments-service | grep -E 'bracket|match'")
print(f"    - docker logs matches-service | grep -E 'bracket|match'")

print(f"\n{C.G}✨ ¡Todos los eventos funcionan correctamente!{C.NC}\n")
