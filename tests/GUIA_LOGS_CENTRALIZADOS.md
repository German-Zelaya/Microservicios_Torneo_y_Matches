# 📋 Guía de Logs Centralizados

## 🎯 Configuración Implementada

Se ha configurado un sistema de **logs centralizados ligero** para todos los microservicios usando el driver `json-file` de Docker con las siguientes características:

### ✨ Características

- ✅ **Rotación automática de logs**: Máximo 10MB por archivo
- ✅ **Retención limitada**: Solo se guardan 3 archivos rotados por servicio
- ✅ **Etiquetas personalizadas**: Cada servicio tiene etiquetas para filtrado fácil
- ✅ **Sin servicios adicionales**: No requiere ELK, Loki, ni otros servicios pesados
- ✅ **Fácil consulta**: Script incluido para visualizar logs de forma organizada

### 🏷️ Etiquetas por Servicio

| Servicio | Tipo | Lenguaje |
|----------|------|----------|
| tournaments-service | tournaments | python |
| matches-service | matches | go |
| auth-service | auth | nodejs |
| teams-service | teams | nodejs |
| notifications-service | notifications | nodejs |
| postgres | database | - |
| mongodb | database | - |
| redis | cache | - |
| rabbitmq | messaging | - |

## 🚀 Uso del Script de Logs

### Instalación

El script `view-logs.sh` ya está listo. Solo asegúrate de tener permisos de ejecución:

```bash
chmod +x view-logs.sh
```

### Comandos Básicos

#### Ver todos los logs
```bash
./view-logs.sh all
```

#### Ver logs solo de microservicios
```bash
./view-logs.sh services
```

#### Ver logs de un servicio específico
```bash
./view-logs.sh tournaments
./view-logs.sh matches
./view-logs.sh auth
./view-logs.sh teams
./view-logs.sh notifications
```

#### Ver logs de bases de datos
```bash
./view-logs.sh databases
./view-logs.sh postgres
./view-logs.sh mongodb
```

#### Ver logs de infraestructura
```bash
./view-logs.sh infrastructure
./view-logs.sh redis
./view-logs.sh rabbitmq
```

### Comandos Avanzados

#### Seguir logs en tiempo real
```bash
./view-logs.sh follow tournaments
./view-logs.sh follow matches
```

#### Ver solo errores
```bash
./view-logs.sh errors
```

#### Ver estadísticas de logs
```bash
./view-logs.sh stats
```

#### Limpiar logs antiguos
```bash
./view-logs.sh clean
```

## 📊 Comandos Docker Compose Directos

Si prefieres usar Docker Compose directamente:

### Ver logs de todos los servicios
```bash
docker-compose logs
```

### Ver logs de un servicio específico
```bash
docker-compose logs tournaments-service
docker-compose logs matches-service
```

### Seguir logs en tiempo real
```bash
docker-compose logs -f tournaments-service
```

### Ver últimas N líneas
```bash
docker-compose logs --tail=50 tournaments-service
```

### Ver logs con timestamp
```bash
docker-compose logs -t tournaments-service
```

### Ver logs desde una fecha específica
```bash
docker-compose logs --since="2024-01-01" tournaments-service
```

### Ver logs de múltiples servicios
```bash
docker-compose logs tournaments-service matches-service
```

## 🔍 Filtrado Avanzado con grep

### Buscar errores
```bash
docker-compose logs | grep -i error
docker-compose logs | grep -iE "error|exception|failed"
```

### Buscar por nivel de log
```bash
docker-compose logs | grep "INFO"
docker-compose logs | grep "ERROR"
docker-compose logs | grep "WARNING"
```

### Buscar en un servicio específico
```bash
docker-compose logs tournaments-service | grep "tournament_id"
docker-compose logs matches-service | grep "match_id"
```

### Contar ocurrencias
```bash
docker-compose logs | grep -c "error"
```

## 📈 Monitoreo de Logs

### Ver tamaño de logs
```bash
docker ps -q | xargs docker inspect --format='{{.Name}} {{.LogPath}}' | while read name path; do
    if [ -f "$path" ]; then
        echo "$name: $(du -h "$path" | cut -f1)"
    fi
done
```

### Verificar configuración de logging
```bash
docker inspect tournaments-service | jq '.[0].HostConfig.LogConfig'
```

### Listar archivos de logs
```bash
sudo ls -lh /var/lib/docker/containers/*/
```

## 🧹 Mantenimiento

### Limpiar logs de un contenedor específico
```bash
truncate -s 0 $(docker inspect --format='{{.LogPath}}' tournaments-service)
```

### Limpiar todos los logs
```bash
docker-compose down
docker system prune -f
```

### Rotar logs manualmente
```bash
docker-compose restart
```

## ⚙️ Configuración Personalizada

Si necesitas ajustar la configuración de logs, edita `docker-compose.yml`:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"    # Cambiar tamaño máximo
    max-file: "3"      # Cambiar cantidad de archivos
```

### Opciones disponibles:
- `max-size`: "1m", "10m", "100m", "1g"
- `max-file`: "1", "3", "5", "10"
- `compress`: "true" (para comprimir logs rotados)

## 🔧 Troubleshooting

### Los logs no aparecen
1. Verifica que el contenedor esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Verifica la configuración de logging:
   ```bash
   docker inspect <container_name> | jq '.[0].HostConfig.LogConfig'
   ```

### Los logs son muy grandes
1. Reduce el `max-size` en `docker-compose.yml`
2. Reduce el `max-file` para guardar menos archivos
3. Ejecuta `./view-logs.sh clean` para limpiar

### No puedo ver logs antiguos
Los logs se rotan automáticamente. Si necesitas retener más logs, aumenta `max-file` en la configuración.

## 💡 Mejores Prácticas

1. **Revisa logs regularmente**: Usa `./view-logs.sh errors` diariamente
2. **Monitorea el tamaño**: Usa `./view-logs.sh stats` para ver estadísticas
3. **Limpia periódicamente**: Ejecuta `./view-logs.sh clean` mensualmente
4. **Usa seguimiento en desarrollo**: `./view-logs.sh follow <servicio>` durante debugging
5. **Etiqueta tus logs**: Los servicios ya tienen etiquetas para facilitar búsquedas

## 🔐 Seguridad

- ⚠️ Los logs pueden contener información sensible
- 🔒 No incluyas contraseñas, tokens o API keys en los logs
- 📝 Revisa que los logs de producción no expongan datos privados
- 🗑️ Limpia logs antiguos regularmente

## 📚 Recursos Adicionales

- [Docker Logging Documentation](https://docs.docker.com/config/containers/logging/)
- [Docker Compose Logs](https://docs.docker.com/compose/reference/logs/)
- [JSON File Logging Driver](https://docs.docker.com/config/containers/logging/json-file/)

## 🎓 Ejemplos de Uso Común

### Debugging de un problema específico
```bash
# Ver logs recientes del servicio con problemas
./view-logs.sh tournaments

# Seguir logs en tiempo real
./view-logs.sh follow tournaments

# Buscar errores específicos
docker-compose logs tournaments-service | grep -i "connection refused"
```

### Monitoreo de producción
```bash
# Ver solo errores de todos los servicios
./view-logs.sh errors

# Ver estadísticas generales
./view-logs.sh stats

# Ver logs de infraestructura
./view-logs.sh infrastructure
```

### Investigación de incidentes
```bash
# Ver logs desde hace 1 hora
docker-compose logs --since=1h

# Ver logs de múltiples servicios relacionados
docker-compose logs tournaments-service matches-service

# Buscar por ID específico
docker-compose logs | grep "tournament_id: 12345"
```

---

**Nota**: Esta configuración es ideal para desarrollo y ambientes pequeños. Para producción a gran escala, considera soluciones como ELK Stack, Grafana Loki, o servicios cloud como AWS CloudWatch.
