# 🎯 Pruebas de Eventos de Bracket y Matches

Este documento describe los scripts de prueba para el flujo completo de brackets y matches en el sistema de torneos.

## 📋 Tabla de Contenidos

- [Eventos a Probar](#eventos-a-probar)
- [Scripts Disponibles](#scripts-disponibles)
- [Requisitos Previos](#requisitos-previos)
- [Uso de los Scripts](#uso-de-los-scripts)
- [Verificación Manual](#verificación-manual)

---

## 🎪 Eventos a Probar

El flujo de brackets y matches involucra 3 eventos principales de RabbitMQ:

| Evento | Productor | Consumidor | Descripción |
|--------|-----------|------------|-------------|
| `tournament.bracket.generated` | **Tournaments** | **Matches** | Crea los matches de la primera ronda cuando se genera el bracket |
| `match.finished` | **Matches** | **Tournaments** | Notifica que un match terminó y avanza al ganador |
| `bracket.update.next_match` | **Tournaments** | **Matches** | Crea/actualiza el match de la siguiente ronda |

### 🔄 Flujo del Proceso

```
1. Usuario crea torneo
   ↓
2. Usuario genera bracket con participantes
   ↓
3. 📤 EVENTO: tournament.bracket.generated
   → Matches Service crea matches de primera ronda
   ↓
4. Matches se completan (resultado reportado)
   ↓
5. 📤 EVENTO: match.finished
   → Tournaments Service procesa ganador
   ↓
6. 📤 EVENTO: bracket.update.next_match
   → Matches Service actualiza match de siguiente ronda
   ↓
7. Se repite desde paso 4 hasta completar todas las rondas
```

---

## 📜 Scripts Disponibles

### 1. `test_bracket_flow.py` - Prueba Completa

**Descripción:** Simula un torneo completo de 4 participantes desde la generación del bracket hasta el match final.

**Características:**
- ✅ Crea un torneo automáticamente
- ✅ Genera bracket con 4 participantes
- ✅ Completa TODOS los matches automáticamente
- ✅ Muestra logs detallados de cada evento
- ✅ Visualiza el estado del bracket en cada ronda
- ✅ Resumen final completo

**Cuándo usar:**
- Para probar el flujo completo end-to-end
- Para verificar que todo funciona correctamente
- Para demos o presentaciones

**Tiempo estimado:** ~2-3 minutos

### 2. `test_bracket_events_quick.py` - Prueba Rápida

**Descripción:** Prueba solo los primeros eventos sin completar todo el torneo.

**Características:**
- ✅ Crea un torneo y genera bracket
- ✅ Completa SOLO el primer match
- ✅ Verifica que los 3 eventos se publiquen
- ✅ Muestra logs relevantes
- ⚡ Más rápido y conciso

**Cuándo usar:**
- Para verificaciones rápidas
- Durante desarrollo
- Para debug de eventos específicos

**Tiempo estimado:** ~30 segundos

---

## 🚀 Requisitos Previos

### 1. Servicios en Ejecución

Asegúrate de que todos los servicios estén corriendo:

```bash
docker compose up -d
```

Verifica que estén todos activos:

```bash
docker compose ps
```

Deberías ver estos servicios como `healthy` o `running`:
- `postgres-esports`
- `mongodb-esports`
- `redis-esports`
- `rabbitmq-esports`
- `tournaments-service`
- `matches-service`
- `auth-service`
- `teams-service`
- `notifications-service`

### 2. Dependencias de Python

Si no las tienes instaladas:

```bash
pip install requests
```

---

## 🎮 Uso de los Scripts

### Opción 1: Prueba Completa (Recomendada)

```bash
./test_bracket_flow.py
```

O:

```bash
python3 test_bracket_flow.py
```

**Qué hace:**
1. Verifica que todos los servicios estén disponibles
2. Crea un torneo de 4 participantes
3. Genera el bracket (crea 2 matches de primera ronda)
4. Completa los 2 matches de primera ronda
5. Completa el match final (ronda 2)
6. Muestra el ganador del torneo

**Salida esperada:**
```
🧪 PRUEBA DE FLUJO COMPLETO DE BRACKETS Y MATCHES

Este script probará:
  1. tournament.bracket.generated → Crea matches iniciales
  2. match.finished → Avanza ganadores
  3. bracket.update.next_match → Actualiza matches de siguiente ronda

✅ Todos los servicios están disponibles

📝 PASO 1: Crear Torneo
✅ Torneo creado exitosamente
   ID: 123
   ...

🎯 PASO 2: Generar Bracket
✅ Bracket generado:
   • Participantes: 4
   • Rondas totales: 2
   • Matches primera ronda: 2
   ...

🎮 SIMULACIÓN DEL FLUJO DE TORNEO
🏆 RONDA 1 de 2
...
```

### Opción 2: Prueba Rápida

```bash
./test_bracket_events_quick.py
```

O:

```bash
python3 test_bracket_events_quick.py
```

**Qué hace:**
1. Crea torneo
2. Genera bracket
3. Completa SOLO el primer match
4. Verifica que los 3 eventos se publiquen

**Salida esperada:**
```
🧪 PRUEBA RÁPIDA: Eventos de Bracket y Matches

Eventos a probar:
  1. tournament.bracket.generated (Tournaments → Matches)
  2. match.finished (Matches → Tournaments)
  3. bracket.update.next_match (Tournaments → Matches)

✅ Torneo creado: ID 124
✅ Bracket generado:
   • Participantes: 4
   • Rondas totales: 2
   • Matches primera ronda: 2
...

✅ PRUEBA COMPLETADA

Eventos verificados:
  ✅ tournament.bracket.generated → Matches creados en primera ronda
  ✅ match.finished → Ganador avanzado a siguiente ronda
  ✅ bracket.update.next_match → Match de ronda 2 actualizado
```

---

## 🔍 Verificación Manual

### 1. Ver Logs en Tiempo Real

**Tournaments Service:**
```bash
docker logs -f tournaments-service | grep -E "bracket|match|📤|📩"
```

**Matches Service:**
```bash
docker logs -f matches-service | grep -E "bracket|match|Creating|Updating"
```

### 2. RabbitMQ Management UI

Abre en tu navegador:
```
http://localhost:15672
```

Credenciales:
- **Usuario:** `guest`
- **Contraseña:** `guest`

**Qué verificar:**
- **Queues:** Verifica que las colas existan y tengan consumidores
- **Exchanges:** Verifica el exchange `tournament_events`
- **Bindings:** Verifica los bindings de las routing keys

### 3. API de Matches

Ver matches de un torneo:
```bash
curl http://localhost:8002/api/matches/tournament/{TOURNAMENT_ID}
```

### 4. API de Tournaments

Ver información de un torneo:
```bash
curl http://localhost:8001/api/v1/tournaments/{TOURNAMENT_ID}
```

---

## 📊 Estructura de Eventos

### tournament.bracket.generated

```json
{
  "event_type": "BRACKET_GENERATED",
  "tournament_id": 123,
  "tournament_name": "Test Tournament",
  "total_participants": 4,
  "total_rounds": 2,
  "first_round_matches": 2,
  "matches": [
    {
      "round": 1,
      "match_number": 1,
      "participant1_id": 101,
      "participant2_id": 102
    },
    {
      "round": 1,
      "match_number": 2,
      "participant1_id": 103,
      "participant2_id": 104
    }
  ]
}
```

### match.finished

```json
{
  "event_type": "MATCH_FINISHED",
  "id": "abc123",
  "tournament_id": 123,
  "round": 1,
  "match_number": 1,
  "winner_id": 101,
  "player1_id": 101,
  "player2_id": 102,
  "score": {
    "101": 2,
    "102": 1
  }
}
```

### bracket.update.next_match

```json
{
  "event_type": "BRACKET_UPDATE_NEXT_MATCH",
  "tournament_id": 123,
  "round": 2,
  "match_number": 1,
  "winner_id": 101,
  "is_player1": true,
  "previous_match_id": "abc123"
}
```

---

## ⚠️ Troubleshooting

### Error: "Connection refused" o servicios no disponibles

**Solución:**
```bash
docker compose up -d
sleep 10  # Espera a que los servicios inicien
./test_bracket_flow.py
```

### Error: "No matches found"

**Causa:** Los eventos no se procesaron correctamente

**Solución:**
1. Verifica los logs de los servicios
2. Verifica que RabbitMQ esté funcionando
3. Reinicia los servicios:
   ```bash
   docker compose restart tournaments-service matches-service
   ```

### Los eventos no aparecen en los logs

**Solución:**
```bash
# Ver TODOS los logs sin filtros
docker logs tournaments-service --tail 50
docker logs matches-service --tail 50
```

### Lentitud en las pruebas

**Causa:** Los servicios pueden tardar en procesar eventos

**Solución:** Los scripts ya incluyen delays apropiados, pero si aún hay problemas:
- Aumenta los `time.sleep()` en los scripts
- Verifica que tu máquina tenga recursos suficientes

---

## 📚 Recursos Adicionales

- **API Docs Tournaments:** http://localhost:8001/docs
- **API Docs Matches:** http://localhost:8002/docs
- **RabbitMQ Management:** http://localhost:15672
- **Documentación completa:** Ver `DOCUMENTACION_PROYECTO.md`
- **Guía de pruebas:** Ver `GUIA_PRUEBAS_RAPIDA.md`

---

## ✅ Checklist de Pruebas

Usa este checklist para verificar que todo funciona:

- [ ] Todos los servicios están corriendo
- [ ] `test_bracket_flow.py` se ejecuta sin errores
- [ ] Se crean matches de primera ronda
- [ ] Los matches se completan correctamente
- [ ] Los ganadores avanzan a la siguiente ronda
- [ ] El torneo finaliza con un ganador
- [ ] Los logs muestran los eventos publicados y recibidos
- [ ] RabbitMQ muestra las colas con consumidores activos

---

## 🎉 ¡Listo!

Ahora tienes todo lo necesario para probar el flujo completo de brackets y matches. 

Si encuentras algún problema, revisa la sección de [Troubleshooting](#⚠️-troubleshooting) o los logs de los servicios.

¡Happy testing! 🚀
