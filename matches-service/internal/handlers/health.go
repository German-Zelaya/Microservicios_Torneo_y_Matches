package handlers

import (
	"context"
	"time"

	"github.com/gofiber/fiber/v2"

	"matches-service/config"
	"matches-service/internal/cache"
	"matches-service/internal/database"
)

// HealthCheck verifica que el servicio esté funcionando
func HealthCheck(c *fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"status":  "healthy",
		"service": config.AppConfig.AppName,
		"version": config.AppConfig.AppVersion,
	})
}

// HealthCheckPostgres verifica la conexión a PostgreSQL
func HealthCheckPostgres(c *fiber.Ctx) error {
	if database.PostgresDB == nil {
		return c.Status(503).JSON(fiber.Map{
			"status":    "unhealthy",
			"database":  "PostgreSQL",
			"connected": false,
			"error":     "Base de datos no inicializada",
		})
	}

	sqlDB, err := database.PostgresDB.DB()
	if err != nil {
		return c.Status(503).JSON(fiber.Map{
			"status":    "unhealthy",
			"database":  "PostgreSQL",
			"connected": false,
			"error":     err.Error(),
		})
	}

	if err := sqlDB.Ping(); err != nil {
		return c.Status(503).JSON(fiber.Map{
			"status":    "unhealthy",
			"database":  "PostgreSQL",
			"connected": false,
			"error":     err.Error(),
		})
	}

	return c.JSON(fiber.Map{
		"status":    "healthy",
		"database":  "PostgreSQL",
		"connected": true,
	})
}

// HealthCheckMongo verifica la conexión a MongoDB
func HealthCheckMongo(c *fiber.Ctx) error {
	if database.MongoClient == nil {
		return c.Status(503).JSON(fiber.Map{
			"status":    "unhealthy",
			"database":  "MongoDB",
			"connected": false,
			"error":     "MongoDB no inicializado",
		})
	}

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	if err := database.MongoClient.Ping(ctx, nil); err != nil {
		return c.Status(503).JSON(fiber.Map{
			"status":    "unhealthy",
			"database":  "MongoDB",
			"connected": false,
			"error":     err.Error(),
		})
	}

	return c.JSON(fiber.Map{
		"status":    "healthy",
		"database":  "MongoDB",
		"connected": true,
	})
}

// HealthCheckRedis verifica la conexión a Redis
func HealthCheckRedis(c *fiber.Ctx) error {
	if !cache.IsConnected() {
		return c.Status(503).JSON(fiber.Map{
			"status":    "unhealthy",
			"service":   "Redis",
			"connected": false,
		})
	}

	return c.JSON(fiber.Map{
		"status":    "healthy",
		"service":   "Redis",
		"connected": true,
	})
}
