# Microservicios_Torneo_y_Matches

Sistema de microservicios para gestión de torneos de eSports con arquitectura basada en eventos.

## 🏗️ Arquitectura

### Microservicios

- **🏆 Tournaments Service** (Python/FastAPI) - Puerto 8001
  - Gestión de torneos
  - Generación de brackets
  - Estados de torneos
  
- **⚔️ Matches Service** (Go/Fiber) - Puerto 8002
  - Gestión de partidas
  - Resultados y validación
  - Seguimiento de estados

- **👤 Auth Service** (Node.js) - Puerto 3000
  - Autenticación y autorización
  - Gestión de usuarios
  
- **👥 Teams Service** (Node.js) - Puerto 3002
  - Gestión de equipos
  - Miembros y roles

- **📧 Notifications Service** (NestJS) - Puerto 3003
  - Notificaciones por email
  - Eventos del sistema

- **🌐 GraphQL Gateway** (Node.js/Apollo) - Puerto 4000
  - **NUEVO**: API unificada con GraphQL
  - Acceso a Torneos y Matches en una sola petición
  - Apollo Studio Explorer integrado

### Infraestructura

- **PostgreSQL** - Base de datos principal
- **MongoDB** - Base de datos para matches
- **Redis** - Caché distribuida
- **RabbitMQ** - Message broker para eventos

## 🚀 GraphQL API Gateway

El proyecto incluye un **API Gateway con GraphQL** que unifica los servicios de Torneos y Matches:

```bash
# Acceder al playground
http://localhost:4000/graphql
```

**Ejemplo de query:**
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
      player1_id
      player2_id
    }
  }
}
```

📚 **[Ver Guía Completa del GraphQL Gateway](./graphql-gateway/GETTING_STARTED.md)**

## 📋 Logs Centralizados

Este proyecto cuenta con un sistema de **logs centralizados ligeros** configurado para todos los microservicios.

### 🚀 Uso Rápido

```bash
# Ver todos los logs
./view-logs.sh all

# Ver logs de un servicio específico
./view-logs.sh tournaments
./view-logs.sh matches

# Seguir logs en tiempo real
./view-logs.sh follow tournaments

# Ver solo errores
./view-logs.sh errors

# Ver estadísticas
./view-logs.sh stats

# Exportar logs a archivos
./export-logs.sh
```

### 📚 Documentación Completa

Para más información sobre el sistema de logs, consulta:
- **[GUIA_LOGS_CENTRALIZADOS.md](./GUIA_LOGS_CENTRALIZADOS.md)** - Guía completa de uso

### ⚙️ Características

- ✅ Rotación automática de logs (10MB max por archivo)
- ✅ Retención de 3 archivos rotados por servicio
- ✅ Etiquetas personalizadas para cada servicio
- ✅ Scripts incluidos para visualización y exportación
- ✅ Sin servicios adicionales pesados (no requiere ELK/Loki)