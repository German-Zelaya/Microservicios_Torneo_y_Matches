package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/redis/go-redis/v9"

	"matches-service/config"
)

var (
	RedisClient *redis.Client
	ctx         = context.Background()
)

// ConnectRedis conecta al servidor Redis
func ConnectRedis(cfg *config.Config) error {
	db, err := strconv.Atoi(cfg.RedisDB)
	if err != nil {
		db = 0
	}

	RedisClient = redis.NewClient(&redis.Options{
		Addr:     cfg.GetRedisAddr(),
		Password: cfg.RedisPassword,
		DB:       db,
	})

	// Verificar conexión
	if err := RedisClient.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("error al conectar a Redis: %w", err)
	}

	log.Println("✅ Conectado a Redis")
	return nil
}

// CloseRedis cierra la conexión a Redis
func CloseRedis() error {
	if RedisClient != nil {
		return RedisClient.Close()
	}
	return nil
}

// IsConnected verifica si Redis está conectado
func IsConnected() bool {
	if RedisClient == nil {
		return false
	}
	return RedisClient.Ping(ctx).Err() == nil
}

// Get obtiene un valor del caché
func Get(key string) (string, error) {
	if !IsConnected() {
		return "", fmt.Errorf("Redis no está conectado")
	}

	val, err := RedisClient.Get(ctx, key).Result()
	if err == redis.Nil {
		return "", nil // Clave no existe
	}
	return val, err
}

// Set guarda un valor en el caché con TTL
func Set(key string, value interface{}, ttl time.Duration) error {
	if !IsConnected() {
		log.Printf("⚠️ Redis no conectado, no se guarda caché para: %s", key)
		return nil // No fallar si Redis no está disponible
	}

	// Serializar a JSON si no es string
	var data string
	switch v := value.(type) {
	case string:
		data = v
	default:
		jsonData, err := json.Marshal(value)
		if err != nil {
			return fmt.Errorf("error al serializar valor: %w", err)
		}
		data = string(jsonData)
	}

	return RedisClient.Set(ctx, key, data, ttl).Err()
}

// Delete elimina una clave del caché
func Delete(key string) error {
	if !IsConnected() {
		return nil
	}
	return RedisClient.Del(ctx, key).Err()
}

// DeletePattern elimina todas las claves que coinciden con un patrón
func DeletePattern(pattern string) error {
	if !IsConnected() {
		return nil
	}

	iter := RedisClient.Scan(ctx, 0, pattern, 0).Iterator()
	for iter.Next(ctx) {
		if err := RedisClient.Del(ctx, iter.Val()).Err(); err != nil {
			return err
		}
	}
	return iter.Err()
}

// GetJSON obtiene un valor del caché y lo deserializa
func GetJSON(key string, dest interface{}) error {
	val, err := Get(key)
	if err != nil {
		return err
	}
	if val == "" {
		return redis.Nil // No existe
	}

	return json.Unmarshal([]byte(val), dest)
}

// SetJSON serializa y guarda un valor en el caché
func SetJSON(key string, value interface{}, ttl time.Duration) error {
	return Set(key, value, ttl)
}

// MatchCacheKey genera la clave de caché para una partida
func MatchCacheKey(id uint) string {
	return fmt.Sprintf("match:%d", id)
}

// MatchListCacheKey genera la clave de caché para una lista de partidas
func MatchListCacheKey(tournamentID *uint, status string, page, pageSize int) string {
	tid := "all"
	if tournamentID != nil {
		tid = fmt.Sprintf("%d", *tournamentID)
	}
	return fmt.Sprintf("matches:list:%s:%s:%d:%d", tid, status, page, pageSize)
}

// InvalidateMatchCache invalida el caché de una partida
func InvalidateMatchCache(id uint) error {
	return Delete(MatchCacheKey(id))
}

// InvalidateMatchListCache invalida todas las listas de partidas
func InvalidateMatchListCache() error {
	return DeletePattern("matches:list:*")
}
