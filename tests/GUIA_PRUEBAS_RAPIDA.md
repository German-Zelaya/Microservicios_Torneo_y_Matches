# 🧪 Guía Rápida de Pruebas de Eventos RabbitMQ

## 🚀 Inicio Rápido

### 1. Verificar que los servicios estén corriendo

```bash
docker ps | grep -E "tournaments-service|matches-service|rabbitmq"
```

Deberías ver algo como:
```
tournaments-service   Up X minutes   0.0.0.0:8001->8001/tcp
matches-service       Up X minutes   0.0.0.0:8002->8002/tcp
rabbitmq-esports      Up X minutes   0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
```

### 2. Ejecutar pruebas automatizadas

```bash
# Prueba simple y rápida (recomendado)
python3 test_events_simple.py
```

Esto probará:
- ✅ Creación de torneo → evento `tournament.created`
- ✅ Actualización → evento `tournament.updated`
- ✅ Cambio de estado → evento `tournament.status.*`
- ✅ Verificación de logs en tiempo real

### 3. Monitorear eventos en vivo

En una terminal aparte, ejecuta:

```bash
./monitor-events.sh
```

Luego, en otra terminal, crea un torneo:

```bash
curl -X POST http://localhost:8001/api/v1/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test en Vivo",
    "game": "Valorant",
    "format": "single_elimination",
    "max_participants": 8
  }'
```

Verás en el monitor:
```
[TOURNAMENTS] 📤 Evento publicado: tournament.created
[MATCHES] 📩 Evento recibido: TOURNAMENT_CREATED
[MATCHES] 🆕 Torneo creado: ID=X, Name=Test en Vivo
```

---

## 📁 Scripts Disponibles

| Script | Descripción | Uso |
|--------|-------------|-----|
| `test_events_simple.py` | Prueba automática completa | `python3 test_events_simple.py` |
| `test_messaging_interactive.py` | Prueba interactiva (requiere auth) | `python3 test_messaging_interactive.py` |
| `test-messaging-events.sh` | Prueba bash completa | `./test-messaging-events.sh` |
| `monitor-events.sh` | Monitor en tiempo real | `./monitor-events.sh` |

---

## 🎯 Eventos Soportados

### Desde Tournaments Service → Matches Service

| Evento | Routing Key | ¿Funciona? |
|--------|-------------|-----------|
| Torneo creado | `tournament.created` | ✅ Sí |
| Torneo actualizado | `tournament.updated` | ✅ Sí |
| Estado cambiado | `tournament.status.*` | ✅ Sí |
| Torneo eliminado | `tournament.deleted` | ✅ Sí |
| Bracket generado | `tournament.bracket.generated` | ⏳ Requiere auth |

### Desde Matches Service → Tournaments Service

| Evento | Routing Key | ¿Funciona? |
|--------|-------------|-----------|
| Match creado | `match.created` | ⏳ Por probar |
| Match iniciado | `match.started` | ⏳ Por probar |
| Match completado | `match.finished` | ⏳ Por probar |
| Resultado reportado | `match.result.reported` | ⏳ Por probar |

---

## 🔍 Ver Logs Manualmente

### Ver logs de Tournaments Service
```bash
# Todos los logs
docker logs tournaments-service

# Solo eventos publicados
docker logs tournaments-service | grep "📤"

# Últimas 50 líneas
docker logs tournaments-service --tail 50
```

### Ver logs de Matches Service
```bash
# Todos los logs
docker logs matches-service

# Solo eventos recibidos
docker logs matches-service | grep "📩"

# En tiempo real
docker logs -f matches-service
```

---

## 🐰 Acceder a RabbitMQ Management

1. Abre en tu navegador: http://localhost:15672
2. Credenciales:
   - **Usuario:** guest
   - **Password:** guest

3. Ve a:
   - **Exchanges** → `tournaments_exchange` → Ver bindings
   - **Queues** → `matches_service_queue` → Ver mensajes
   - **Connections** → Ver servicios conectados

---

## ⚡ Prueba Manual Rápida

### 1. Crear un torneo
```bash
curl -X POST http://localhost:8001/api/v1/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Torneo Test",
    "game": "League of Legends",
    "format": "single_elimination",
    "max_participants": 8
  }'
```

### 2. Ver el evento en matches-service
```bash
docker logs matches-service --tail 10 | grep "TOURNAMENT_CREATED"
```

### 3. Actualizar el torneo
```bash
curl -X PUT http://localhost:8001/api/v1/tournaments/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Descripción actualizada"
  }'
```

### 4. Ver el evento de actualización
```bash
docker logs matches-service --tail 10 | grep "TOURNAMENT_UPDATED"
```

---

## 🎓 Conceptos Clave

### Exchange Topic
- Tipo: **Topic**
- Nombre: `tournaments_exchange`
- Permite routing flexible con patrones
- Ejemplo: `tournament.status.*` matchea con:
  - `tournament.status.registration`
  - `tournament.status.in_progress`
  - `tournament.status.completed`

### Persistencia
- Los mensajes son **persistentes** (no se pierden si RabbitMQ se reinicia)
- Las colas son **durables** (sobreviven reinicios)
- Delivery mode: `persistent`

### Acknowledgments
- Los consumidores envían **ack manual** después de procesar
- Si falla el procesamiento, el mensaje se **reencola**
- Garantiza que no se pierdan eventos

---

## 🔧 Troubleshooting

### Problema: "No se conecta a RabbitMQ"

**Verificar que RabbitMQ esté corriendo:**
```bash
docker ps | grep rabbitmq
```

**Ver logs de RabbitMQ:**
```bash
docker logs rabbitmq-esports --tail 50
```

### Problema: "No se reciben eventos"

**Verificar que el consumer esté activo:**
```bash
docker logs matches-service | grep "Consumer iniciado"
```

**Verificar bindings en RabbitMQ:**
```bash
docker exec rabbitmq-esports rabbitmqctl list_bindings
```

### Problema: "Error 400 al iniciar torneo"

Esto es normal si no tienes usuarios en el auth-service. Usa el script simple:
```bash
python3 test_events_simple.py
```

Este script NO requiere autenticación y solo prueba los eventos básicos.

---

## 📚 Documentación Completa

Para información detallada sobre los resultados de las pruebas, ve a:
- **[PRUEBAS_EVENTOS_RABBITMQ.md](./PRUEBAS_EVENTOS_RABBITMQ.md)** - Resultados completos

---

## ✅ Checklist de Pruebas

- [x] Servicios corriendo en Docker
- [x] RabbitMQ conectado
- [x] Evento `tournament.created` funciona
- [x] Evento `tournament.updated` funciona
- [x] Evento `tournament.status.*` funciona
- [ ] Evento `tournament.bracket.generated` (pendiente auth)
- [ ] Eventos de matches (por implementar consumer en tournaments)

---

**¿Necesitas ayuda?** Revisa los logs o abre el RabbitMQ Management UI.
