import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class ExternalServicesClient:
    """Cliente para comunicarse con servicios externos (Auth y Teams)"""

    def __init__(self):
        """Inicializa el cliente con las URLs de los servicios"""
        # URLs de los servicios (configurables via env)
        self.auth_service_url = getattr(settings, 'AUTH_SERVICE_URL', 'http://localhost:3000')
        self.teams_service_url = getattr(settings, 'TEAMS_SERVICE_URL', 'http://localhost:3002')

        # Credenciales para Auth Service
        self.auth_email = getattr(settings, 'AUTH_SERVICE_EMAIL', 'service@tournaments.com')
        self.auth_password = getattr(settings, 'AUTH_SERVICE_PASSWORD', 'service123')

        # Token JWT cacheado
        self._auth_token: Optional[str] = None

        # Timeout para requests
        self.timeout = 10.0

    async def _get_auth_token(self) -> str:
        """
        Obtiene un token JWT del Auth Service.
        Primero intenta registrar el usuario de servicio, luego hace login.
        """
        if self._auth_token:
            return self._auth_token

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Intentar registrar el usuario de servicio (por si no existe)
            try:
                register_url = f"{self.auth_service_url}/api/auth/register"
                await client.post(register_url, json={
                    "username": "tournaments_service",
                    "email": self.auth_email,
                    "password": self.auth_password
                })
            except Exception:
                pass  # Si ya existe, ignoramos el error

            # Hacer login para obtener token
            login_url = f"{self.auth_service_url}/api/auth/login"
            response = await client.post(login_url, json={
                "email": self.auth_email,
                "password": self.auth_password
            })

            if response.status_code == 200:
                data = response.json()
                self._auth_token = data.get('accessToken') or data.get('token')
                logger.info("✅ Token JWT obtenido del Auth Service")
                return self._auth_token
            else:
                logger.error(f"❌ Error al obtener token: {response.status_code}")
                raise ConnectionError(f"No se pudo autenticar con Auth Service: {response.text}")

    async def validate_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Valida que un usuario exista en el Auth Service.

        Args:
            user_id: ID del usuario a validar

        Returns:
            Datos del usuario si existe, None si no existe
        """
        try:
            # Obtener token JWT
            token = await self._get_auth_token()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.auth_service_url}/api/users/{user_id}"
                headers = {"Authorization": f"Bearer {token}"}
                logger.info(f"🔍 Validando usuario {user_id} en Auth Service...")

                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"✅ Usuario {user_id} válido: {user_data.get('username', 'N/A')}")
                    return user_data
                elif response.status_code == 404:
                    logger.warning(f"❌ Usuario {user_id} no encontrado")
                    return None
                elif response.status_code in [401, 403]:
                    # Token expirado, limpiar cache e intentar de nuevo
                    logger.warning("⚠️ Token expirado, renovando...")
                    self._auth_token = None
                    token = await self._get_auth_token()
                    headers = {"Authorization": f"Bearer {token}"}
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        user_data = response.json()
                        logger.info(f"✅ Usuario {user_id} válido: {user_data.get('username', 'N/A')}")
                        return user_data
                    return None
                else:
                    logger.error(f"❌ Error al validar usuario {user_id}: {response.status_code}")
                    return None

        except httpx.ConnectError:
            logger.error(f"❌ No se pudo conectar al Auth Service en {self.auth_service_url}")
            raise ConnectionError(f"Auth Service no disponible en {self.auth_service_url}")
        except Exception as e:
            logger.error(f"❌ Error al validar usuario {user_id}: {e}")
            raise

    async def validate_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Valida que un equipo exista en el Teams Service.

        Args:
            team_id: ID del equipo a validar

        Returns:
            Datos del equipo si existe, None si no existe
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.teams_service_url}/api/teams/{team_id}"
                logger.info(f"🔍 Validando equipo {team_id} en Teams Service...")

                response = await client.get(url)

                if response.status_code == 200:
                    team_data = response.json()
                    logger.info(f"✅ Equipo {team_id} válido: {team_data.get('name', 'N/A')}")
                    return team_data
                elif response.status_code == 404:
                    logger.warning(f"❌ Equipo {team_id} no encontrado")
                    return None
                else:
                    logger.error(f"❌ Error al validar equipo {team_id}: {response.status_code}")
                    return None

        except httpx.ConnectError:
            logger.error(f"❌ No se pudo conectar al Teams Service en {self.teams_service_url}")
            raise ConnectionError(f"Teams Service no disponible en {self.teams_service_url}")
        except Exception as e:
            logger.error(f"❌ Error al validar equipo {team_id}: {e}")
            raise

    async def validate_users(self, user_ids: List[str]) -> Dict[str, Any]:
        """
        Valida múltiples usuarios en el Auth Service.

        Args:
            user_ids: Lista de IDs de usuarios a validar

        Returns:
            Dict con 'valid_users', 'invalid_users' y 'all_valid'
        """
        valid_users = []
        invalid_users = []

        for user_id in user_ids:
            user = await self.validate_user(str(user_id))
            if user:
                valid_users.append({
                    'id': user_id,
                    'username': user.get('username'),
                    'role': user.get('role')
                })
            else:
                invalid_users.append(user_id)

        result = {
            'valid_users': valid_users,
            'invalid_users': invalid_users,
            'all_valid': len(invalid_users) == 0,
            'total_validated': len(valid_users),
            'total_invalid': len(invalid_users)
        }

        if invalid_users:
            logger.warning(f"⚠️ Usuarios inválidos encontrados: {invalid_users}")
        else:
            logger.info(f"✅ Todos los usuarios ({len(valid_users)}) son válidos")

        return result

    async def validate_teams(self, team_ids: List[str]) -> Dict[str, Any]:
        """
        Valida múltiples equipos en el Teams Service.

        Args:
            team_ids: Lista de IDs de equipos a validar

        Returns:
            Dict con 'valid_teams', 'invalid_teams' y 'all_valid'
        """
        valid_teams = []
        invalid_teams = []

        for team_id in team_ids:
            team = await self.validate_team(str(team_id))
            if team:
                valid_teams.append({
                    'id': team_id,
                    'name': team.get('name'),
                    'captain_id': team.get('captainId')
                })
            else:
                invalid_teams.append(team_id)

        result = {
            'valid_teams': valid_teams,
            'invalid_teams': invalid_teams,
            'all_valid': len(invalid_teams) == 0,
            'total_validated': len(valid_teams),
            'total_invalid': len(invalid_teams)
        }

        if invalid_teams:
            logger.warning(f"⚠️ Equipos inválidos encontrados: {invalid_teams}")
        else:
            logger.info(f"✅ Todos los equipos ({len(valid_teams)}) son válidos")

        return result

    async def validate_participants(
        self,
        participant_ids: List[int],
        tournament_type: str
    ) -> Dict[str, Any]:
        """
        Valida participantes según el tipo de torneo.

        Args:
            participant_ids: Lista de IDs de participantes
            tournament_type: 'individual' para usuarios, 'team' para equipos

        Returns:
            Resultado de la validación
        """
        if tournament_type == 'individual':
            return await self.validate_users([str(id) for id in participant_ids])
        elif tournament_type == 'team':
            return await self.validate_teams([str(id) for id in participant_ids])
        else:
            raise ValueError(f"Tipo de torneo no válido: {tournament_type}. Use 'individual' o 'team'")

    async def check_auth_service_health(self) -> bool:
        """Verifica si el Auth Service está disponible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.auth_service_url}/health")
                return response.status_code == 200
        except:
            return False

    async def check_teams_service_health(self) -> bool:
        """Verifica si el Teams Service está disponible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.teams_service_url}/health")
                return response.status_code == 200
        except:
            return False


# Instancia global del cliente
external_services = ExternalServicesClient()
