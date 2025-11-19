# Sistema de Torneos y Matches - Microservicios

## Descripción General

Sistema de gestión de torneos de eSports basado en microservicios. Permite crear torneos individuales (1v1) y por equipos, con generación automática de brackets de eliminación simple.

---

## Arquitectura

### Microservicios

| Servicio | Puerto | Tecnología | Base de Datos | Descripción |
|----------|--------|------------|---------------|-------------|
| Auth Service | 3000 | Node.js/Express | PostgreSQL (auth_db) | Autenticación y gestión de usuarios |
| Teams Service | 3002 | Node.js/Express | PostgreSQL (teams_db) | Gestión de equipos y miembros |
| Tournaments Service | 8001 | Python/FastAPI | PostgreSQL (tournaments_db) | Gestión de torneos y brackets |
| Matches Service | 8002 | Go/Fiber | PostgreSQL (matches_db) + MongoDB | Gestión de partidas y resultados |

### Infraestructura

- **PostgreSQL**: Bases de datos relacionales
- **MongoDB**: Almacenamiento de logs/históricos de matches
- **Redis**: Caché compartido
- **RabbitMQ**: Mensajería entre servicios (eventos)

---

## Flujo del Sistema

### 1. Torneo Individual (1v1)

```
1. Crear usuarios (Auth Service)
2. Login para obtener JWT con UUID del usuario
3. Crear torneo tipo "individual"
4. Iniciar torneo con lista de UUIDs de usuarios
5. Se generan matches automáticamente via RabbitMQ
6. Para cada match:
   - Iniciar match (PATCH /start)
   - Reportar resultado (POST /result)
   - Validar resultado (PUT /validate)
7. Los ganadores avanzan automáticamente a la siguiente ronda
8. El sistema detecta la final y no crea matches extra
```

### 2. Torneo de Equipos

```
1. Crear usuarios (Auth Service)
2. Crear equipos con capitán (Teams Service)
3. Invitar miembros al equipo (requiere JWT)
4. Aceptar invitaciones con token
5. Crear torneo tipo "team"
6. Iniciar torneo con lista de UUIDs de equipos
7. Mismo flujo de matches que individual
```

---

## Endpoints Principales

### Auth Service (puerto 3000)

```
POST /api/auth/register     - Registrar usuario
POST /api/auth/login        - Login (devuelve JWT con UUID)
GET  /api/users/{id}        - Obtener usuario (requiere JWT)
```

### Teams Service (puerto 3002)

```
POST   /api/teams                    - Crear equipo
GET    /api/teams/{id}               - Obtener equipo con miembros
POST   /api/teams/{id}/invite        - Invitar miembro (requiere JWT)
POST   /api/teams/{id}/accept/{token} - Aceptar invitación
DELETE /api/teams/{id}/members/{userId} - Expulsar miembro
```

### Tournaments Service (puerto 8001)

```
POST  /api/v1/tournaments           - Crear torneo
GET   /api/v1/tournaments           - Listar torneos
GET   /api/v1/tournaments/{id}      - Obtener torneo
PATCH /api/v1/tournaments/{id}/status?new_status=registration - Cambiar estado
POST  /api/v1/tournaments/{id}/start - Iniciar torneo (genera bracket)
```

### Matches Service (puerto 8002)

```
GET   /api/v1/matches?tournament_id={id} - Listar matches de torneo
GET   /api/v1/matches/{id}               - Obtener match
PATCH /api/v1/matches/{id}/start         - Iniciar match
POST  /api/v1/matches/{id}/result        - Reportar resultado
PUT   /api/v1/matches/{id}/validate      - Validar resultado (referee)
```

---

## Comunicación entre Servicios

### Eventos RabbitMQ

| Evento | Productor | Consumidor | Descripción |
|--------|-----------|------------|-------------|
| tournament.bracket.generated | Tournaments | Matches | Crear matches de primera ronda |
| match.finished | Matches | Tournaments | Avanzar ganador a siguiente ronda |
| bracket.update.next_match | Tournaments | Matches | Crear/actualizar match siguiente ronda |

### Validación HTTP

- Tournaments Service valida usuarios en Auth Service
- Tournaments Service valida equipos en Teams Service
- Teams Service valida usuarios en Auth Service al invitar

---

## Configuración

### Variables de Entorno Importantes

**Tournaments Service:**
```
DATABASE_URL=postgresql://postgres:super124man@localhost:5432/tournaments_db
AUTH_SERVICE_URL=http://localhost:3000
TEAMS_SERVICE_URL=http://localhost:3002
RABBITMQ_HOST=localhost
```

**Matches Service:**
```
POSTGRES_HOST=localhost
POSTGRES_DB=matches_db
RABBITMQ_HOST=localhost
```

**Teams Service:**
```
AUTH_SERVICE_URL=http://localhost:3000
RABBITMQ_URL=amqp://guest:guest@localhost:5672
```

---

## Ejecución

### Local

1. Iniciar PostgreSQL, MongoDB, Redis, RabbitMQ
2. Ejecutar migración de matches:
```sql
-- En matches_db
ALTER TABLE matches
    ALTER COLUMN player1_id TYPE VARCHAR(36),
    ALTER COLUMN player2_id TYPE VARCHAR(36),
    ALTER COLUMN winner_id TYPE VARCHAR(36);
```

3. Iniciar cada servicio:
```bash
# Auth Service
cd auth-service-main && npm start

# Teams Service
cd teams-service-main && npm start

# Tournaments Service
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Matches Service
cd matches-service && go run cmd/main.go
```

### Docker

```bash
docker-compose up --build
```

---

## Cálculo de Rondas y Matches

El sistema usa eliminación simple:

| Participantes | Rondas | Matches Totales |
|---------------|--------|-----------------|
| 2 | 1 | 1 |
| 4 | 2 | 3 |
| 8 | 3 | 7 |
| 16 | 4 | 15 |

Fórmula:
- Rondas = log₂(participantes)
- Total matches = participantes - 1

---

## Modelo de Datos

### Match
```json
{
  "id": 1,
  "tournament_id": 1,
  "round": 1,
  "match_number": 1,
  "player1_id": "uuid-string",
  "player2_id": "uuid-string",
  "winner_id": "uuid-string",
  "player1_score": 3,
  "player2_score": 1,
  "status": "completed",
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "notes": "Notas del match"
}
```

### Estados de Match
- `scheduled` - Programado
- `in_progress` - En progreso
- `pending_validation` - Esperando validación
- `completed` - Completado
- `cancelled` - Cancelado

### Estados de Torneo
- `pending` - Pendiente
- `registration` - Abierto a inscripciones
- `in_progress` - En curso
- `completed` - Finalizado
- `cancelled` - Cancelado

---

## Trabajo Pendiente para Notifications Service

### Responsabilidades

El microservicio de notificaciones debe:

1. **Escuchar eventos de RabbitMQ:**
   - `match.created` - Notificar que hay un nuevo match
   - `match.started` - Notificar que el match comenzó
   - `match.finished` - Notificar resultado y ganador
   - `team.member.invited` - Notificar invitación a equipo

2. **Consultar Teams Service** para obtener miembros del equipo y decidir a quién notificar

3. **Tipos de notificación:**
   - Email
   - Push notifications
   - In-app notifications

### Ejemplo de Flujo

```
Match Finalizado
    → RabbitMQ (match.finished)
    → Notifications Service
        → GET Teams Service para obtener miembros
        → Enviar notificación a todos los miembros del equipo ganador/perdedor
```

### Datos disponibles en eventos

El evento `match.finished` incluye:
```json
{
  "id": 1,
  "tournament_id": 1,
  "round": 1,
  "match_number": 1,
  "player1_id": "uuid-equipo-o-usuario",
  "player2_id": "uuid-equipo-o-usuario",
  "winner_id": "uuid-ganador",
  "player1_score": 3,
  "player2_score": 1
}
```

---

## Notas Técnicas Importantes

1. **UUIDs**: Todos los IDs de usuarios y equipos son UUIDs (strings de 36 caracteres)

2. **Autenticación**: El Teams Service requiere JWT en el header para invitar miembros:
   ```
   Authorization: Bearer <token>
   ```

3. **Migración**: Ejecutar la migración SQL en matches_db para cambiar player_ids de integer a varchar(36)

4. **Final del torneo**: El sistema detecta automáticamente cuándo es la final y no crea matches adicionales

5. **Validación de participantes**: Al iniciar un torneo, se validan todos los UUIDs contra Auth Service (individual) o Teams Service (equipos)

---

## Contacto

Para dudas sobre la implementación, revisar los archivos:
- `app/services/bracket_service.py` - Lógica de generación de brackets
- `app/services/match_consumer.py` - Consumidor de eventos de matches
- `matches-service/internal/messaging/consumer.go` - Consumidor en Go
- `matches-service/internal/services/match_service.go` - Lógica de negocio de matches
