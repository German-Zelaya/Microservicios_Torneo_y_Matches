package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"

	"matches-service/config"
	"matches-service/internal/cache"
	"matches-service/internal/database"
	"matches-service/internal/handlers"
	"matches-service/internal/messaging"
	"matches-service/internal/models"
)

func main() {
	// Cargar configuración
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("❌ Error al cargar configuración: %v", err)
	}

	log.Printf("🚀 Iniciando %s v%s\n", cfg.AppName, cfg.AppVersion)

	// Conectar a PostgreSQL
	log.Println("📊 Conectando a PostgreSQL...")
	if err := database.ConnectPostgres(cfg); err != nil {
		log.Fatalf("❌ Error al conectar a PostgreSQL: %v", err)
	}
	defer func() {
		if err := database.ClosePostgres(); err != nil {
			log.Printf("❌ Error al cerrar PostgreSQL: %v", err)
		}
	}()

	// Ejecutar migraciones
	log.Println("🔄 Ejecutando migraciones...")
	if err := database.AutoMigrate(&models.Match{}, &models.Result{}); err != nil {
		log.Fatalf("❌ Error en migraciones: %v", err)
	}

	// Conectar a MongoDB
	log.Println("📊 Conectando a MongoDB...")
	if err := database.ConnectMongo(cfg); err != nil {
		log.Printf("⚠️  Error al conectar a MongoDB: %v", err)
		log.Println("⚠️  Continuando sin MongoDB...")
	} else {
		defer func() {
			if err := database.CloseMongo(); err != nil {
				log.Printf("❌ Error al cerrar MongoDB: %v", err)
			}
		}()
	}

	// Conectar a Redis
	log.Println("🔄 Conectando a Redis...")
	if err := cache.ConnectRedis(cfg); err != nil {
		log.Printf("⚠️  Error al conectar a Redis: %v", err)
		log.Println("⚠️  Continuando sin caché...")
	} else {
		defer func() {
			if err := cache.CloseRedis(); err != nil {
				log.Printf("❌ Error al cerrar Redis: %v", err)
			}
		}()
	}

	// Conectar a RabbitMQ (Producer)
	log.Println("📢 Conectando a RabbitMQ (Producer)...")
	if err := messaging.ConnectProducer(cfg); err != nil {
		log.Printf("⚠️  Error al conectar Producer: %v", err)
		log.Println("⚠️  Los eventos no se publicarán...")
	} else {
		defer func() {
			if err := messaging.CloseProducer(); err != nil {
				log.Printf("❌ Error al cerrar Producer: %v", err)
			}
		}()
	}

	// Conectar a RabbitMQ (Consumer)
	log.Println("👂 Conectando a RabbitMQ (Consumer)...")
	if err := messaging.ConnectConsumer(cfg); err != nil {
		log.Printf("⚠️  Error al conectar Consumer: %v", err)
		log.Println("⚠️  No se consumirán eventos...")
	} else {
		defer func() {
			if err := messaging.CloseConsumer(); err != nil {
				log.Printf("❌ Error al cerrar Consumer: %v", err)
			}
		}()

		// Iniciar consumo de eventos
		if err := messaging.StartConsuming(); err != nil {
			log.Printf("⚠️  Error al iniciar consumer: %v", err)
		}
	}

	// Crear aplicación Fiber
	app := fiber.New(fiber.Config{
		AppName: fmt.Sprintf("%s v%s", cfg.AppName, cfg.AppVersion),
	})

	// Middlewares
	app.Use(recover.New())
	app.Use(logger.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins: "*",
		AllowMethods: "GET,POST,PUT,PATCH,DELETE,OPTIONS",
		AllowHeaders: "Origin,Content-Type,Accept,Authorization",
	}))

	// Rutas básicas
	app.Get("/", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"service": cfg.AppName,
			"version": cfg.AppVersion,
			"status":  "running",
		})
	})

	// Health checks
	app.Get("/health", handlers.HealthCheck)
	app.Get("/health/postgres", handlers.HealthCheckPostgres)
	app.Get("/health/mongo", handlers.HealthCheckMongo)
	app.Get("/health/redis", handlers.HealthCheckRedis)

	// API v1 routes
	api := app.Group("/api/v1")

	// Match routes
	matchHandler := handlers.NewMatchHandler()
	matches := api.Group("/matches")
	{
		matches.Post("/", matchHandler.CreateMatch)
		matches.Get("/", matchHandler.GetMatches)
		matches.Get("/:id", matchHandler.GetMatch)
		matches.Put("/:id", matchHandler.UpdateMatch)
		matches.Delete("/:id", matchHandler.DeleteMatch)
		matches.Patch("/:id/start", matchHandler.StartMatch)
		matches.Patch("/:id/complete", matchHandler.CompleteMatch)
		matches.Patch("/:id/cancel", matchHandler.CancelMatch)
		matches.Post("/:id/result", matchHandler.ReportResult)      // Reportar resultado
		matches.Put("/:id/validate", matchHandler.ValidateResult)   // Validar resultado
	}

	// Iniciar servidor
	port := cfg.Port
	log.Printf("🌐 Servidor escuchando en puerto %s", port)
	log.Printf("📚 Endpoints disponibles:")
	log.Printf("  - http://localhost:%s/", port)
	log.Printf("  - http://localhost:%s/api/v1/matches", port)

	// Manejo de señales para shutdown graceful
	go func() {
		if err := app.Listen(":" + port); err != nil {
			log.Fatalf("❌ Error al iniciar servidor: %v", err)
		}
	}()

	// Esperar señal de interrupción
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit

	log.Println("👋 Cerrando servidor...")
	if err := app.Shutdown(); err != nil {
		log.Printf("❌ Error al cerrar servidor: %v", err)
	}

	log.Println("✅ Servidor cerrado correctamente")
}
