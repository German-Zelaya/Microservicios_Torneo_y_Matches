package database

import (
	"fmt"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"matches-service/config"
)

var PostgresDB *gorm.DB

// ConnectPostgres conecta a la base de datos PostgreSQL
func ConnectPostgres(cfg *config.Config) error {
	dsn := cfg.GetPostgresDSN()

	// Configurar logger de GORM
	var gormLogger logger.Interface
	if cfg.AppEnv == "development" {
		gormLogger = logger.Default.LogMode(logger.Info)
	} else {
		gormLogger = logger.Default.LogMode(logger.Silent)
	}

	// Conectar a PostgreSQL
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: gormLogger,
	})

	if err != nil {
		return fmt.Errorf("error al conectar a PostgreSQL: %w", err)
	}

	// Verificar conexión
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("error al obtener DB de GORM: %w", err)
	}

	if err := sqlDB.Ping(); err != nil {
		return fmt.Errorf("error al hacer ping a PostgreSQL: %w", err)
	}

	// Configurar pool de conexiones
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)

	PostgresDB = db
	log.Println("✅ Conectado a PostgreSQL")

	return nil
}

// ClosePostgres cierra la conexión a PostgreSQL
func ClosePostgres() error {
	if PostgresDB != nil {
		sqlDB, err := PostgresDB.DB()
		if err != nil {
			return err
		}
		return sqlDB.Close()
	}
	return nil
}

// AutoMigrate ejecuta las migraciones automáticas
func AutoMigrate(models ...interface{}) error {
	if PostgresDB == nil {
		return fmt.Errorf("PostgreSQL no está conectado")
	}

	log.Println("🔄 Ejecutando migraciones automáticas...")
	if err := PostgresDB.AutoMigrate(models...); err != nil {
		return fmt.Errorf("error en migraciones: %w", err)
	}

	log.Println("✅ Migraciones completadas")
	return nil
}
