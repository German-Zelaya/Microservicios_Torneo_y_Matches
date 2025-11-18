import math
import logging
from typing import List, Dict, Any
import asyncio

from app.models.tournament import Tournament, TournamentStatus
from app.services.messaging_service import rabbitmq_service

logger = logging.getLogger(__name__)


class BracketService:
    """Servicio para generar y gestionar brackets de torneos"""
    
    @staticmethod
    def calculate_rounds(num_participants: int) -> int:
        """
        Calcula el número de rondas necesarias para un torneo de eliminación simple.
        
        Args:
            num_participants: Número de participantes
            
        Returns:
            Número de rondas
        """
        if num_participants <= 1:
            return 0
        return math.ceil(math.log2(num_participants))
    
    @staticmethod
    def generate_bracket_structure(participants: List[int]) -> List[Dict[str, Any]]:
        """
        Genera la estructura del bracket para un torneo de eliminación simple.
        
        Args:
            participants: Lista de IDs de participantes
            
        Returns:
            Lista de matches a crear
        """
        num_participants = len(participants)
        
        if num_participants < 2:
            raise ValueError("Se necesitan al menos 2 participantes para generar brackets")
        
        # Calcular la siguiente potencia de 2
        next_power_of_2 = 2 ** math.ceil(math.log2(num_participants))
        
        # Calcular cuántos "byes" necesitamos (participantes que pasan automáticamente)
        num_byes = next_power_of_2 - num_participants
        
        matches = []
        match_number = 1
        round_num = 1
        
        # Crear la primera ronda
        participant_idx = 0
        
        # Primero, crear matches para participantes sin bye
        num_first_round_matches = (num_participants - num_byes) // 2
        
        for i in range(num_first_round_matches):
            match = {
                "round": round_num,
                "match_number": match_number,
                "player1_id": participants[participant_idx],
                "player2_id": participants[participant_idx + 1],
            }
            matches.append(match)
            match_number += 1
            participant_idx += 2
        
        # Los participantes restantes tienen bye (pasan automáticamente a la siguiente ronda)
        # Estos se agregarán cuando se creen las siguientes rondas
        
        logger.info(f"Generados {len(matches)} matches para la primera ronda")
        logger.info(f"Participantes con bye: {num_byes}")
        
        return matches
    
    @staticmethod
    async def start_tournament(tournament: Tournament, participant_ids: List[int]) -> Dict[str, Any]:
        """
        Inicia un torneo generando el bracket y publicando eventos para crear matches.
        
        Args:
            tournament: Torneo a iniciar
            participant_ids: Lista de IDs de participantes
            
        Returns:
            Información del bracket generado
        """
        try:
            # Validar que el torneo esté en estado apropiado
            if tournament.status != TournamentStatus.REGISTRATION:
                raise ValueError(f"El torneo debe estar en estado 'registration'. Estado actual: {tournament.status}")
            
            # Validar número de participantes
            num_participants = len(participant_ids)
            if num_participants < 2:
                raise ValueError("Se necesitan al menos 2 participantes para iniciar el torneo")
            
            if num_participants > tournament.max_participants:
                raise ValueError(f"Número de participantes ({num_participants}) excede el máximo ({tournament.max_participants})")
            
            # Generar estructura del bracket
            matches = BracketService.generate_bracket_structure(participant_ids)
            
            # Calcular información del bracket
            total_rounds = BracketService.calculate_rounds(num_participants)
            
            # Publicar evento para que Matches Service cree las partidas
            bracket_data = {
                "tournament_id": tournament.id,
                "tournament_name": tournament.name,
                "total_participants": num_participants,
                "total_rounds": total_rounds,
                "first_round_matches": len(matches),
                "matches": matches
            }
            
            # Publicar evento
            await rabbitmq_service.publish_event(
                routing_key="tournament.bracket.generated",
                event_data=bracket_data,
                event_type="BRACKET_GENERATED"
            )
            
            logger.info(f"✅ Bracket generado para torneo {tournament.id}: {len(matches)} matches en primera ronda")
            
            return {
                "tournament_id": tournament.id,
                "total_participants": num_participants,
                "total_rounds": total_rounds,
                "first_round_matches": len(matches),
                "matches_generated": len(matches),
                "status": "bracket_generated"
            }
            
        except Exception as e:
            logger.error(f"❌ Error al generar bracket: {e}")
            raise
    
    @staticmethod
    def get_bracket_info(num_participants: int) -> Dict[str, Any]:
        """
        Obtiene información sobre cómo sería el bracket sin generarlo.
        
        Args:
            num_participants: Número de participantes
            
        Returns:
            Información del bracket
        """
        if num_participants < 2:
            return {
                "valid": False,
                "message": "Se necesitan al menos 2 participantes"
            }
        
        next_power_of_2 = 2 ** math.ceil(math.log2(num_participants))
        num_byes = next_power_of_2 - num_participants
        total_rounds = BracketService.calculate_rounds(num_participants)
        first_round_matches = (num_participants - num_byes) // 2
        
        return {
            "valid": True,
            "total_participants": num_participants,
            "total_rounds": total_rounds,
            "participants_with_bye": num_byes,
            "first_round_matches": first_round_matches,
            "total_matches": num_participants - 1  # En eliminación simple, total de matches = n - 1
        }