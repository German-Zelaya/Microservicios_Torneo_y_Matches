# 🧪 Guía de Pruebas - Sistema de Torneos y Matches

## 📋 FASE 4: Pruebas del Flujo Completo

Esta guía te ayudará a probar todo el sistema de torneos con actualización automática de brackets.

---

## 🚀 Preparación

### 1. Asegúrate de tener los últimos cambios

```bash
git pull
```

### 2. Levanta los servicios

```bash
docker-compose down
docker-compose up --build
```

Espera a que todos los servicios estén listos. Deberías ver:
- ✅ Tournaments Service en puerto 8001
- ✅ Matches Service en puerto 8002
- ✅ PostgreSQL, MongoDB, Redis, RabbitMQ conectados
- ✅ Consumers iniciados y escuchando eventos

---

## 🎯 Opción 1: Prueba Automática (Recomendado)

Ejecuta el script de pruebas completo:

```bash
chmod +x test-complete-flow.sh
./test-complete-flow.sh
```

Este script:
1. ✅ Crea un torneo
2. ✅ Genera brackets con 4 participantes
3. ✅ Juega todos los matches de la Ronda 1 (semifinales)
4. ✅ Verifica que se cree automáticamente el match de la Final
5. ✅ Juega la Final
6. ✅ Muestra un resumen completo

**Qué esperar:**
- El script debería completarse sin errores
- Verás mensajes en verde ✅ confirmando cada paso
- Al final verás el CAMPEÓN del torneo
- Todos los checks deberían pasar

---

## 🧪 Opción 2: Prueba Manual Paso a Paso

### **Paso 1: Crear un torneo**

```bash
curl -X POST http://localhost:8001/api/v1/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Torneo Manual de Prueba",
    "game": "Valorant",
    "max_participants": 8,
    "description": "Prueba manual del sistema"
  }'
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "name": "Torneo Manual de Prueba",
  "status": "pending",
  ...
}
```

Anota el `id` del torneo (ejemplo: `1`)

---

### **Paso 2: Cambiar estado a registration**

```bash
curl -X PATCH http://localhost:8001/api/v1/tournaments/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "registration"}'
```

---

### **Paso 3: Iniciar el torneo (Generar brackets)**

```bash
curl -X POST http://localhost:8001/api/v1/tournaments/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": [1, 2, 3, 4]
  }'
```

**Qué sucede:**
- 🔄 Se generan 2 matches en la Ronda 1
- 📤 Se publica evento `tournament.bracket.generated`
- 👂 Matches Service escucha y crea los matches
- ✅ Torneo cambia a estado `in_progress`

**Verifica en logs:**
```
tournaments-service_1  | 📤 Evento publicado: tournament.bracket.generated
matches-service_1      | 📩 Evento recibido: BRACKET_GENERATED
matches-service_1      | ✅ Match 1 creado: Round 1, Match 1
matches-service_1      | ✅ Match 2 creado: Round 1, Match 2
```

---

### **Paso 4: Ver matches creados**

```bash
curl http://localhost:8002/api/v1/matches?tournament_id=1 | jq
```

**Respuesta esperada:**
```json
{
  "matches": [
    {
      "id": 1,
      "round": 1,
      "match_number": 1,
      "player1_id": 1,
      "player2_id": 2,
      "status": "scheduled",
      ...
    },
    {
      "id": 2,
      "round": 1,
      "match_number": 2,
      "player1_id": 3,
      "player2_id": 4,
      "status": "scheduled",
      ...
    }
  ],
  "total": 2
}
```

---

### **Paso 5: Jugar Match 1 (Semifinal 1)**

#### 5.1 Iniciar el match
```bash
curl -X PATCH http://localhost:8002/api/v1/matches/1/start
```

**Estado:** `scheduled` → `in_progress`

---

#### 5.2 Reportar resultado
```bash
curl -X POST http://localhost:8002/api/v1/matches/1/result \
  -H "Content-Type: application/json" \
  -d '{
    "player1_score": 10,
    "player2_score": 5,
    "winner_id": 1,
    "notes": "Victoria de Player 1"
  }'
```

**Qué sucede:**
- ✅ Resultado registrado
- 🔄 Estado cambia a `pending_validation`
- 📤 Se publica evento `match.result.reported`

**Verifica en logs:**
```
matches-service_1  | 📤 Evento publicado: match.result.reported
```

---

#### 5.3 Validar resultado ⭐ **AQUÍ EMPIEZA LA MAGIA**
```bash
curl -X PUT http://localhost:8002/api/v1/matches/1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "Resultado verificado"
  }'
```

**Qué sucede:**
- ✅ Match completado (estado: `completed`)
- 📤 **Matches Service publica:** `match.finished`
- 👂 **Tournaments Service escucha** el evento
- 🧮 **Tournaments calcula** siguiente ronda
- 📤 **Tournaments publica:** `bracket.update.next_match`
- 👂 **Matches Service escucha** y crea/actualiza match de Ronda 2
- 🎯 **Player 1 avanza automáticamente a la Final**

**Verifica en logs (IMPORTANTE):**
```
# Matches Service publica evento
matches-service_1      | 📤 Evento publicado: match.finished

# Tournaments Service procesa
tournaments-service_1  | 🎯 Procesando evento match.finished
tournaments-service_1  | 🏆 Avanzando ganador 1 a siguiente ronda
tournaments-service_1  | 🎯 Siguiente match: Ronda=2, Match=1, Posición=Player1
tournaments-service_1  | 📤 Evento publicado: bracket.update.next_match

# Matches Service crea el siguiente match
matches-service_1      | 📩 Evento recibido: BRACKET_UPDATE_NEXT_MATCH
matches-service_1      | 🏆 Actualizando bracket: Torneo=1, Ronda=2, Match=1, Ganador=1
matches-service_1      | 📝 Match no existe, creando nuevo match...
matches-service_1      | ✅ Match creado: ID=3, Round=2, Match=1
```

---

### **Paso 6: Jugar Match 2 (Semifinal 2)**

Repite el proceso para el Match 2:

```bash
# 6.1 Iniciar
curl -X PATCH http://localhost:8002/api/v1/matches/2/start

# 6.2 Reportar resultado (gana Player 3)
curl -X POST http://localhost:8002/api/v1/matches/2/result \
  -H "Content-Type: application/json" \
  -d '{
    "player1_score": 8,
    "player2_score": 12,
    "winner_id": 3,
    "notes": "Victoria de Player 3"
  }'

# 6.3 Validar
curl -X PUT http://localhost:8002/api/v1/matches/2/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "Resultado verificado"
  }'
```

**Qué sucede:**
- 🏆 Player 3 avanza a la Final
- 🔄 El match de la Final (ID=3) se **actualiza** con Player 3
- ✅ Ahora el match de Final tiene ambos jugadores: Player 1 vs Player 3

**Verifica en logs:**
```
matches-service_1  | 📝 Match existe (ID=3), actualizando jugador...
matches-service_1  | ✅ Match actualizado: ID=3
matches-service_1  | 🎮 Match completo con ambos jugadores (P1=1, P2=3), listo para ser jugado
```

---

### **Paso 7: Verificar el bracket actualizado**

```bash
curl http://localhost:8002/api/v1/matches?tournament_id=1 | jq '.matches[] | {id, round, match_number, player1_id, player2_id, winner_id, status}'
```

**Deberías ver:**
```json
[
  {
    "id": 1,
    "round": 1,
    "match_number": 1,
    "player1_id": 1,
    "player2_id": 2,
    "winner_id": 1,
    "status": "completed"
  },
  {
    "id": 2,
    "round": 1,
    "match_number": 2,
    "player1_id": 3,
    "player2_id": 4,
    "winner_id": 3,
    "status": "completed"
  },
  {
    "id": 3,
    "round": 2,          ← CREADO AUTOMÁTICAMENTE
    "match_number": 1,
    "player1_id": 1,     ← GANADOR DEL MATCH 1
    "player2_id": 3,     ← GANADOR DEL MATCH 2
    "winner_id": null,
    "status": "scheduled"
  }
]
```

✅ **¡El bracket se actualizó automáticamente!**

---

### **Paso 8: Jugar la Final**

```bash
# 8.1 Iniciar Final
curl -X PATCH http://localhost:8002/api/v1/matches/3/start

# 8.2 Reportar resultado (gana Player 1)
curl -X POST http://localhost:8002/api/v1/matches/3/result \
  -H "Content-Type: application/json" \
  -d '{
    "player1_score": 15,
    "player2_score": 10,
    "winner_id": 1,
    "notes": "¡Player 1 es el CAMPEÓN!"
  }'

# 8.3 Validar y coronar al campeón
curl -X PUT http://localhost:8002/api/v1/matches/3/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "CAMPEÓN DEL TORNEO"
  }'
```

---

## 🎉 Verificación Final

### Ver estado final del torneo

```bash
curl http://localhost:8002/api/v1/matches?tournament_id=1 | jq
```

**Debes ver:**
- ✅ 2 matches completados en Ronda 1
- ✅ 1 match completado en Ronda 2 (Final)
- ✅ Todos con sus ganadores asignados
- ✅ Bracket completo desde semifinales hasta campeón

---

## 🐰 Verificar eventos en RabbitMQ

Abre el panel de administración:
- URL: http://localhost:15672
- Usuario: `guest`
- Password: `guest`

Ve a **Queues**:
- `matches_service_queue` - Eventos procesados por Matches Service
- `tournaments_service_queue` - Eventos procesados por Tournaments Service

En **Exchanges** → `tournaments_exchange`:
- Verás todos los eventos publicados
- Routing keys: `match.finished`, `bracket.update.next_match`

---

## ✅ Checklist de Validación

Marca cada punto a medida que lo pruebes:

- [ ] Crear torneo ✅
- [ ] Generar brackets con participantes ✅
- [ ] Ver matches creados automáticamente ✅
- [ ] Iniciar un match (scheduled → in_progress) ✅
- [ ] Reportar resultado (in_progress → pending_validation) ✅
- [ ] Validar resultado (pending_validation → completed) ✅
- [ ] Ver evento `match.finished` en logs ✅
- [ ] Ver creación automática de match de siguiente ronda ✅
- [ ] Completar todos los matches de una ronda ✅
- [ ] Verificar que el match de siguiente ronda tiene ambos jugadores ✅
- [ ] Jugar y completar la final ✅
- [ ] Ver bracket completo con todos los ganadores ✅

---

## 🔍 Debugging

### Si algo falla, verifica:

1. **Servicios levantados:**
   ```bash
   docker-compose ps
   ```
   Todos deben estar "Up"

2. **Logs en tiempo real:**
   ```bash
   docker-compose logs -f tournaments-service
   docker-compose logs -f matches-service
   ```

3. **RabbitMQ conectado:**
   ```bash
   curl http://localhost:8001/health/rabbitmq
   curl http://localhost:8002/health
   ```

4. **Base de datos:**
   ```bash
   curl http://localhost:8001/health/db
   curl http://localhost:8002/health/postgres
   ```

---

## 📊 Casos de Prueba Adicionales

### Probar rechazo de resultado

```bash
# Reportar resultado
curl -X POST http://localhost:8002/api/v1/matches/1/result \
  -H "Content-Type: application/json" \
  -d '{
    "player1_score": 10,
    "player2_score": 5,
    "winner_id": 1,
    "notes": "Resultado con error"
  }'

# Rechazar resultado
curl -X PUT http://localhost:8002/api/v1/matches/1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "notes": "Puntaje incorrecto, reportar nuevamente"
  }'

# Verificar que volvió a in_progress con puntajes en 0
curl http://localhost:8002/api/v1/matches/1
```

---

## 🎓 Conceptos Clave Probados

### FASE 1 y 2: Reportar y Validar
- ✅ Separación entre reportar resultado y validarlo
- ✅ Estados intermedios (pending_validation)
- ✅ Flujo de aprobación/rechazo

### FASE 3: Brackets Automáticos
- ✅ Event-driven architecture con RabbitMQ
- ✅ Comunicación entre microservicios
- ✅ Actualización automática de brackets
- ✅ Algoritmo de bracket de eliminación simple

### Algoritmo de Bracket
```
Match 1 (impar)  ──┐
                   ├──→ Match 1 de Ronda 2 (Player1)
Match 2 (par)   ──┘

Match 3 (impar)  ──┐
                   ├──→ Match 2 de Ronda 2 (Player1)
Match 4 (par)   ──┘
```

---

## 🚀 Conclusión

Si todas las pruebas pasan, ¡felicidades! Has implementado exitosamente:

✅ Sistema completo de torneos
✅ Reportar y validar resultados
✅ Actualización automática de brackets
✅ Arquitectura de microservicios con eventos
✅ Integración RabbitMQ

**¡Sistema listo para producción!** 🎉
