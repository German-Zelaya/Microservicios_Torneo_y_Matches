# Ejemplos de Queries y Mutations GraphQL

Este archivo contiene ejemplos de todas las operaciones disponibles en el API Gateway GraphQL.

## 📋 QUERIES

### 1. Health Checks

```graphql
# Verificar estado del Gateway y servicios
query HealthChecks {
  health
  healthTournaments
  healthMatches
}
```

### 2. Listar Torneos (con paginación)

```graphql
query ListTournaments {
  tournaments(page: 1, page_size: 10) {
    tournaments {
      id
      name
      game
      description
      status
      tournament_type
      max_participants
      current_participants
      registration_start
      registration_end
      tournament_start
      tournament_end
      created_at
      updated_at
    }
    total
    page
    page_size
    total_pages
  }
}
```

### 3. Filtrar Torneos por Juego

```graphql
query FilterTournamentsByGame {
  tournaments(page: 1, page_size: 10, game: "Valorant") {
    tournaments {
      id
      name
      game
      status
      current_participants
      max_participants
    }
    total
  }
}
```

### 4. Filtrar Torneos por Estado

```graphql
query FilterTournamentsByStatus {
  tournaments(page: 1, page_size: 10, status: in_progress) {
    tournaments {
      id
      name
      game
      status
      current_participants
    }
    total
  }
}
```

### 5. Obtener Torneo Específico

```graphql
query GetTournament {
  tournament(id: 1) {
    id
    name
    game
    description
    status
    tournament_type
    max_participants
    current_participants
    registration_start
    registration_end
    tournament_start
    tournament_end
    created_at
    updated_at
  }
}
```

### 6. Obtener Torneo con sus Matches

```graphql
query GetTournamentWithMatches {
  tournament(id: 1) {
    id
    name
    game
    status
    current_participants
    max_participants
    matches {
      id
      round
      position
      status
      player1_id
      player2_id
      winner_id
      scheduled_time
      start_time
      end_time
      created_at
    }
  }
}
```

### 7. Listar Matches

```graphql
query ListMatches {
  matches {
    matches {
      id
      tournament_id
      round
      position
      status
      player1_id
      player2_id
      winner_id
      scheduled_time
      start_time
      end_time
      created_at
      updated_at
    }
    total
  }
}
```

### 8. Filtrar Matches por Torneo

```graphql
query FilterMatchesByTournament {
  matches(tournament_id: 1) {
    matches {
      id
      round
      position
      status
      player1_id
      player2_id
      winner_id
    }
    total
  }
}
```

### 9. Filtrar Matches por Estado y Ronda

```graphql
query FilterMatchesByStatusAndRound {
  matches(tournament_id: 1, status: in_progress, round: 1) {
    matches {
      id
      round
      position
      status
      player1_id
      player2_id
    }
    total
  }
}
```

### 10. Obtener Match Específico

```graphql
query GetMatch {
  match(id: "550e8400-e29b-41d4-a716-446655440000") {
    id
    tournament_id
    round
    position
    status
    player1_id
    player2_id
    winner_id
    scheduled_time
    start_time
    end_time
    created_at
    updated_at
  }
}
```

### 11. Obtener Match con Torneo y Resultado

```graphql
query GetMatchWithDetails {
  match(id: "550e8400-e29b-41d4-a716-446655440000") {
    id
    round
    position
    status
    player1_id
    player2_id
    winner_id
    start_time
    end_time
    tournament {
      id
      name
      game
      status
    }
    result {
      id
      player1_score
      player2_score
      reporter_id
      validated
      validated_by
      validated_at
      notes
      created_at
    }
  }
}
```

## 🔧 MUTATIONS

### 1. Crear Torneo Individual

```graphql
mutation CreateIndividualTournament {
  createTournament(input: {
    name: "Torneo Valorant 2024"
    game: "Valorant"
    description: "Torneo competitivo de Valorant"
    max_participants: 16
    tournament_type: individual
    registration_start: "2024-12-01T00:00:00Z"
    registration_end: "2024-12-15T23:59:59Z"
    tournament_start: "2024-12-20T10:00:00Z"
    tournament_end: "2024-12-22T18:00:00Z"
  }) {
    id
    name
    game
    status
    tournament_type
    max_participants
    created_at
  }
}
```

### 2. Crear Torneo por Equipos

```graphql
mutation CreateTeamTournament {
  createTournament(input: {
    name: "Liga de Equipos CS:GO"
    game: "Counter-Strike: Global Offensive"
    description: "Torneo profesional de equipos"
    max_participants: 8
    tournament_type: team
  }) {
    id
    name
    game
    status
    tournament_type
    max_participants
    created_at
  }
}
```

### 3. Actualizar Torneo

```graphql
mutation UpdateTournament {
  updateTournament(
    id: 1
    input: {
      name: "Torneo Valorant 2024 - Actualizado"
      description: "Torneo competitivo de Valorant con premios"
      max_participants: 32
    }
  ) {
    id
    name
    description
    max_participants
    updated_at
  }
}
```

### 4. Cambiar Estado a "Abierto a Inscripciones"

```graphql
mutation OpenRegistration {
  changeTournamentStatus(id: 1, status: registration) {
    id
    name
    status
    updated_at
  }
}
```

### 5. Iniciar Torneo (Generar Bracket)

```graphql
mutation StartTournament {
  startTournament(
    id: 1
    input: {
      participant_ids: [
        "user-uuid-1",
        "user-uuid-2",
        "user-uuid-3",
        "user-uuid-4",
        "user-uuid-5",
        "user-uuid-6",
        "user-uuid-7",
        "user-uuid-8"
      ]
    }
  ) {
    tournament_id
    total_rounds
    total_matches
    matches {
      match_id
      round
      position
      player1_id
      player2_id
      next_match_id
    }
  }
}
```

### 6. Cambiar Estado a "En Progreso"

```graphql
mutation MarkInProgress {
  changeTournamentStatus(id: 1, status: in_progress) {
    id
    name
    status
    updated_at
  }
}
```

### 7. Cambiar Estado a "Completado"

```graphql
mutation CompleteTournament {
  changeTournamentStatus(id: 1, status: completed) {
    id
    name
    status
    updated_at
  }
}
```

### 8. Cancelar Torneo

```graphql
mutation CancelTournament {
  changeTournamentStatus(id: 1, status: cancelled) {
    id
    name
    status
    updated_at
  }
}
```

### 9. Eliminar Torneo

```graphql
mutation DeleteTournament {
  deleteTournament(id: 1)
}
```

### 10. Crear Match Manualmente

```graphql
mutation CreateMatch {
  createMatch(input: {
    tournament_id: 1
    round: 1
    position: 1
    player1_id: "user-uuid-1"
    player2_id: "user-uuid-2"
    scheduled_time: "2024-12-20T14:00:00Z"
  }) {
    id
    tournament_id
    round
    position
    status
    player1_id
    player2_id
    scheduled_time
    created_at
  }
}
```

### 11. Actualizar Match

```graphql
mutation UpdateMatch {
  updateMatch(
    id: "match-uuid"
    input: {
      scheduled_time: "2024-12-20T15:00:00Z"
      player1_id: "new-player-uuid"
    }
  ) {
    id
    player1_id
    player2_id
    scheduled_time
    updated_at
  }
}
```

### 12. Iniciar Match

```graphql
mutation StartMatch {
  startMatch(id: "match-uuid") {
    id
    status
    start_time
    updated_at
  }
}
```

### 13. Reportar Resultado de Match

```graphql
mutation ReportMatchResult {
  reportResult(
    id: "match-uuid"
    input: {
      player1_score: 13
      player2_score: 11
      reporter_id: "admin-user-id"
      notes: "Partido muy reñido, sin incidencias"
    }
  ) {
    id
    match_id
    player1_score
    player2_score
    reporter_id
    validated
    notes
    created_at
  }
}
```

### 14. Validar Resultado

```graphql
mutation ValidateMatchResult {
  validateResult(id: "match-uuid") {
    id
    match_id
    player1_score
    player2_score
    validated
    validated_by
    validated_at
  }
}
```

### 15. Completar Match

```graphql
mutation CompleteMatch {
  completeMatch(id: "match-uuid") {
    id
    status
    winner_id
    end_time
    updated_at
  }
}
```

### 16. Cancelar Match

```graphql
mutation CancelMatch {
  cancelMatch(id: "match-uuid") {
    id
    status
    updated_at
  }
}
```

### 17. Eliminar Match

```graphql
mutation DeleteMatch {
  deleteMatch(id: "match-uuid")
}
```

## 🔄 FLUJOS COMPLETOS

### Flujo 1: Crear y Comenzar un Torneo

```graphql
# Paso 1: Crear torneo
mutation Step1CreateTournament {
  createTournament(input: {
    name: "Copa Valorant Diciembre"
    game: "Valorant"
    max_participants: 8
    tournament_type: individual
  }) {
    id
    name
    status
  }
}

# Paso 2: Abrir inscripciones
mutation Step2OpenRegistration {
  changeTournamentStatus(id: 1, status: registration) {
    id
    status
  }
}

# Paso 3: Iniciar torneo con participantes
mutation Step3StartTournament {
  startTournament(
    id: 1
    input: {
      participant_ids: [
        "player-1", "player-2", "player-3", "player-4",
        "player-5", "player-6", "player-7", "player-8"
      ]
    }
  ) {
    tournament_id
    total_rounds
    total_matches
    matches {
      match_id
      round
      position
      player1_id
      player2_id
    }
  }
}

# Paso 4: Consultar torneo con matches generados
query Step4CheckTournament {
  tournament(id: 1) {
    id
    name
    status
    current_participants
    matches {
      id
      round
      position
      status
      player1_id
      player2_id
    }
  }
}
```

### Flujo 2: Jugar un Match

```graphql
# Paso 1: Iniciar match
mutation Step1StartMatch {
  startMatch(id: "match-uuid") {
    id
    status
    start_time
  }
}

# Paso 2: Reportar resultado
mutation Step2ReportResult {
  reportResult(
    id: "match-uuid"
    input: {
      player1_score: 13
      player2_score: 7
      reporter_id: "referee-id"
    }
  ) {
    id
    player1_score
    player2_score
    validated
  }
}

# Paso 3: Validar resultado
mutation Step3ValidateResult {
  validateResult(id: "match-uuid") {
    id
    validated
    validated_by
  }
}

# Paso 4: Completar match
mutation Step4CompleteMatch {
  completeMatch(id: "match-uuid") {
    id
    status
    winner_id
    end_time
  }
}

# Paso 5: Verificar actualización
query Step5CheckMatch {
  match(id: "match-uuid") {
    id
    status
    winner_id
    result {
      player1_score
      player2_score
      validated
    }
    tournament {
      name
      status
    }
  }
}
```

## 📝 Notas

- Reemplaza los IDs de ejemplo (`1`, `"match-uuid"`, etc.) con IDs reales de tu sistema
- Los timestamps deben estar en formato ISO 8601
- Los UUIDs de usuarios/equipos deben existir en los servicios correspondientes
- Algunos campos son opcionales y se pueden omitir
- El estado del torneo debe ser apropiado para cada operación
