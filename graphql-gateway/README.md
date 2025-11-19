# GraphQL Gateway - Torneos y Matches

API Gateway con GraphQL que unifica los microservicios de Torneos y Matches.

## 🚀 Características

- **GraphQL API** unificada para Torneos y Matches
- **Apollo Server** con Express
- Consultas y mutaciones para ambos servicios
- Field resolvers para relaciones entre entidades
- Health checks para todos los servicios
- Manejo centralizado de errores

## 📋 Requisitos Previos

- Node.js 18+ 
- npm o yarn
- Servicios de Torneos y Matches ejecutándose

## 🔧 Instalación

```bash
# Instalar dependencias
npm install
```

## ⚙️ Configuración

Crea un archivo `.env` basado en `.env.example`:

```env
PORT=4000
NODE_ENV=development

# Microservices URLs
TOURNAMENTS_SERVICE_URL=http://localhost:8001
MATCHES_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:3000
TEAMS_SERVICE_URL=http://localhost:3002
```

## 🏃 Ejecución

```bash
# Desarrollo (con hot-reload)
npm run dev

# Producción
npm start
```

El servidor estará disponible en: `http://localhost:4000/graphql`

## 📚 Uso del API

### GraphQL Playground

Abre tu navegador en `http://localhost:4000/graphql` para acceder al Apollo Studio Explorer.

### Ejemplos de Queries

#### 1. Listar Torneos

```graphql
query GetTournaments {
  tournaments(page: 1, page_size: 10) {
    tournaments {
      id
      name
      game
      status
      current_participants
      max_participants
      created_at
    }
    total
    total_pages
  }
}
```

#### 2. Obtener un Torneo con sus Matches

```graphql
query GetTournamentWithMatches {
  tournament(id: 1) {
    id
    name
    game
    status
    matches {
      id
      round
      position
      status
      player1_id
      player2_id
      winner_id
    }
  }
}
```

#### 3. Listar Matches de un Torneo

```graphql
query GetMatchesByTournament {
  matches(tournament_id: 1) {
    matches {
      id
      round
      position
      status
      player1_id
      player2_id
      winner_id
      tournament {
        id
        name
        game
      }
    }
    total
  }
}
```

#### 4. Obtener un Match con su Torneo

```graphql
query GetMatchWithTournament {
  match(id: "match-uuid-here") {
    id
    round
    status
    player1_id
    player2_id
    winner_id
    tournament {
      id
      name
      game
      status
    }
    result {
      player1_score
      player2_score
      validated
      reporter_id
    }
  }
}
```

### Ejemplos de Mutations

#### 1. Crear un Torneo

```graphql
mutation CreateTournament {
  createTournament(input: {
    name: "Torneo Valorant 2024"
    game: "Valorant"
    description: "Torneo competitivo de Valorant"
    max_participants: 16
    tournament_type: individual
  }) {
    id
    name
    game
    status
    max_participants
  }
}
```

#### 2. Iniciar un Torneo

```graphql
mutation StartTournament {
  startTournament(
    id: 1
    input: {
      participant_ids: [
        "player-1",
        "player-2",
        "player-3",
        "player-4"
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
```

#### 3. Actualizar Estado de Torneo

```graphql
mutation ChangeTournamentStatus {
  changeTournamentStatus(id: 1, status: registration) {
    id
    name
    status
  }
}
```

#### 4. Iniciar un Match

```graphql
mutation StartMatch {
  startMatch(id: "match-uuid-here") {
    id
    status
    start_time
  }
}
```

#### 5. Reportar Resultado de Match

```graphql
mutation ReportResult {
  reportResult(
    id: "match-uuid-here"
    input: {
      player1_score: 13
      player2_score: 8
      reporter_id: "admin-user-id"
      notes: "Partido disputado sin incidencias"
    }
  ) {
    id
    match_id
    player1_score
    player2_score
    validated
    reporter_id
  }
}
```

#### 6. Validar Resultado

```graphql
mutation ValidateResult {
  validateResult(id: "match-uuid-here") {
    id
    validated
    validated_by
    validated_at
  }
}
```

#### 7. Completar un Match

```graphql
mutation CompleteMatch {
  completeMatch(id: "match-uuid-here") {
    id
    status
    winner_id
    end_time
  }
}
```

### Health Checks

```graphql
query HealthChecks {
  health
  healthTournaments
  healthMatches
}
```

## 🏗️ Arquitectura

```
graphql-gateway/
├── src/
│   ├── config.js           # Configuración del servidor
│   ├── schema.js           # Definiciones de tipos GraphQL
│   ├── resolvers.js        # Resolvers de queries y mutations
│   ├── server.js           # Servidor Apollo Server
│   └── datasources/
│       ├── tournaments.js  # Cliente API de Torneos
│       └── matches.js      # Cliente API de Matches
├── .env                    # Variables de entorno
└── package.json           # Dependencias
```

## 🔄 Flujo de Datos

1. Cliente envía query/mutation GraphQL al Gateway
2. Apollo Server procesa la petición
3. Resolver correspondiente llama al DataSource apropiado
4. DataSource hace petición HTTP al microservicio REST
5. Respuesta se transforma al formato GraphQL
6. Cliente recibe respuesta unificada

## 🐛 Debugging

Ver logs en consola para:
- Peticiones GraphQL recibidas
- Llamadas a microservicios
- Errores y excepciones

## 🔒 Seguridad

Para producción, considera agregar:
- Autenticación JWT
- Rate limiting
- Query complexity analysis
- CORS configurado apropiadamente

## 📝 Notas

- El Gateway actúa como proxy, no almacena datos
- Los microservicios mantienen su lógica de negocio
- Ideal para clientes que prefieren GraphQL sobre REST
- Soporta queries anidadas (tournament → matches, match → tournament)

## 🤝 Integración con Docker

Para usar en Docker Compose, actualizar las URLs en `.env`:

```env
TOURNAMENTS_SERVICE_URL=http://tournaments-service:8001
MATCHES_SERVICE_URL=http://matches-service:8002
AUTH_SERVICE_URL=http://auth-service:3000
TEAMS_SERVICE_URL=http://teams-service:3002
```
