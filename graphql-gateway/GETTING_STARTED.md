# 🌐 GraphQL API Gateway - Guía de Inicio

## ✨ Descripción

El **GraphQL Gateway** es una capa de abstracción que unifica los microservicios de **Torneos** y **Matches** bajo una única API GraphQL. Permite a los clientes hacer queries complejas y obtener exactamente los datos que necesitan en una sola petición.

## 🎯 Ventajas del GraphQL Gateway

### 1. **Una sola petición para múltiples recursos**
En lugar de hacer múltiples llamadas REST:
```
GET /api/v1/tournaments/1
GET /api/v1/matches?tournament_id=1
```

Con GraphQL obtienes todo en una sola query:
```graphql
query {
  tournament(id: 1) {
    id
    name
    status
    matches {
      id
      round
      status
    }
  }
}
```

### 2. **Solicita solo lo que necesitas**
No más over-fetching o under-fetching. El cliente decide qué campos necesita.

### 3. **Fuertemente tipado**
GraphQL proporciona un esquema claro y validación automática.

### 4. **Exploración interactiva**
Apollo Studio Explorer permite probar queries directamente en el navegador.

### 5. **Relaciones entre entidades**
Navega fácilmente entre torneos y matches sin preocuparte por las llamadas a diferentes servicios.

## 🚀 Inicio Rápido

### Opción 1: Desarrollo Local

```bash
# 1. Navegar al directorio
cd graphql-gateway

# 2. Instalar dependencias (si no están instaladas)
npm install

# 3. Configurar variables de entorno
cp .env .env.local
# Editar .env.local según tu configuración

# 4. Iniciar en modo desarrollo
npm run dev
```

El servidor estará disponible en: **http://localhost:4000/graphql**

### Opción 2: Con Docker Compose

El GraphQL Gateway ya está incluido en el `docker-compose.yml`:

```bash
# Iniciar todos los servicios incluyendo el Gateway
docker compose up -d

# Ver logs del Gateway
docker compose logs -f graphql-gateway

# Detener todos los servicios
docker compose down
```

El servidor estará disponible en: **http://localhost:4000/graphql**

## 📚 Primeros Pasos

### 1. Verificar que el Gateway está funcionando

Abre tu navegador en: **http://localhost:4000/graphql**

Deberías ver el Apollo Studio Explorer.

### 2. Hacer tu primera query

```graphql
query HelloWorld {
  health
}
```

### 3. Listar torneos

```graphql
query ListTournaments {
  tournaments(page: 1, page_size: 10) {
    tournaments {
      id
      name
      game
      status
    }
    total
  }
}
```

### 4. Crear un torneo

```graphql
mutation CreateTournament {
  createTournament(input: {
    name: "Mi Primer Torneo"
    game: "Valorant"
    max_participants: 8
    tournament_type: individual
  }) {
    id
    name
    status
  }
}
```

## 📖 Documentación Completa

- **[README.md](./README.md)** - Información general y arquitectura
- **[EXAMPLES.md](./EXAMPLES.md)** - Ejemplos de queries y mutations
- **[Schema](./src/schema.js)** - Definición completa del esquema GraphQL

## 🔍 Explorar el Esquema

En Apollo Studio Explorer, puedes:

1. **Ver el esquema completo** - Click en "Schema" en la barra lateral
2. **Autocompletar** - Empieza a escribir y usa `Ctrl+Space`
3. **Ver documentación inline** - Hover sobre cualquier tipo o campo
4. **Ejecutar queries** - Click en el botón "Run" o presiona `Ctrl+Enter`

## 🔄 Flujos de Trabajo Comunes

### Crear y gestionar un torneo

```graphql
# 1. Crear torneo
mutation {
  createTournament(input: {
    name: "Copa Valorant 2024"
    game: "Valorant"
    max_participants: 16
    tournament_type: individual
  }) {
    id
    name
  }
}

# 2. Abrir inscripciones
mutation {
  changeTournamentStatus(id: 1, status: registration) {
    id
    status
  }
}

# 3. Iniciar torneo
mutation {
  startTournament(id: 1, input: {
    participant_ids: ["player1", "player2", "player3", "player4"]
  }) {
    tournament_id
    total_matches
  }
}

# 4. Ver torneo con sus matches
query {
  tournament(id: 1) {
    name
    status
    matches {
      id
      round
      player1_id
      player2_id
      status
    }
  }
}
```

## 🧪 Testing

### Health Checks

```graphql
query {
  health
  healthTournaments
  healthMatches
}
```

### Con curl

```bash
# Query
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { tournaments(page: 1, page_size: 5) { total } }"
  }'

# Mutation
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createTournament(input: { name: \"Test\", game: \"Valorant\" }) { id } }"
  }'
```

## 🔧 Configuración

### Variables de Entorno

```env
PORT=4000
NODE_ENV=development

# URLs de los microservicios
TOURNAMENTS_SERVICE_URL=http://localhost:8001
MATCHES_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:3000
TEAMS_SERVICE_URL=http://localhost:3002
```

### Para Docker

```env
TOURNAMENTS_SERVICE_URL=http://tournaments-service:8001
MATCHES_SERVICE_URL=http://matches-service:8002
AUTH_SERVICE_URL=http://auth-service:3000
TEAMS_SERVICE_URL=http://teams-service:3002
```

## 🐛 Troubleshooting

### El Gateway no se conecta a los servicios

1. Verifica que los microservicios estén corriendo:
```bash
curl http://localhost:8001/health  # Tournaments
curl http://localhost:8002/health  # Matches
```

2. Verifica las URLs en el archivo `.env`

### Error: "Cannot connect to service"

- Asegúrate de que todos los servicios backend estén iniciados
- Verifica que los puertos no estén bloqueados
- En Docker, usa nombres de servicio en lugar de `localhost`

### El playground no carga

- Verifica que el puerto 4000 esté libre
- Intenta acceder a http://localhost:4000/health
- Revisa los logs: `docker compose logs graphql-gateway`

## 📊 Arquitectura

```
┌─────────────────┐
│   Cliente Web   │
│   o Móvil       │
└────────┬────────┘
         │
         │ GraphQL
         ▼
┌─────────────────────┐
│  GraphQL Gateway    │
│  (Apollo Server)    │
│  Puerto: 4000       │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────┐   ┌────────┐
│Torneos│   │Matches │
│ :8001 │   │ :8002  │
└───────┘   └────────┘
  (REST)      (REST)
```

## 🎓 Aprender Más

- [GraphQL Official Documentation](https://graphql.org/)
- [Apollo Server Documentation](https://www.apollographql.com/docs/apollo-server/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)

## 🤝 Contribuir

Para agregar nuevas funcionalidades:

1. Actualizar el schema en `src/schema.js`
2. Agregar resolvers en `src/resolvers.js`
3. Actualizar datasources si es necesario
4. Documentar en `EXAMPLES.md`

## 📝 Notas Importantes

- El Gateway no almacena datos, solo los enruta
- Los microservicios mantienen su lógica de negocio
- Ideal para clientes web y móviles que prefieren GraphQL
- Soporta queries complejas y anidadas
- Caché puede implementarse en el futuro para mejorar rendimiento
