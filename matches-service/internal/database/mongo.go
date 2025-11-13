package database

import (
	"context"
	"fmt"
	"log"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"

	"matches-service/config"
)

var (
	MongoClient *mongo.Client
	MongoDB     *mongo.Database
)

// ConnectMongo conecta a MongoDB
func ConnectMongo(cfg *config.Config) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Crear cliente
	clientOptions := options.Client().ApplyURI(cfg.GetMongoURI())
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return fmt.Errorf("error al conectar a MongoDB: %w", err)
	}

	// Verificar conexión
	if err := client.Ping(ctx, nil); err != nil {
		return fmt.Errorf("error al hacer ping a MongoDB: %w", err)
	}

	MongoClient = client
	MongoDB = client.Database(cfg.MongoDB)

	log.Println("✅ Conectado a MongoDB")
	return nil
}

// CloseMongo cierra la conexión a MongoDB
func CloseMongo() error {
	if MongoClient != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		if err := MongoClient.Disconnect(ctx); err != nil {
			return err
		}
		log.Println("👋 Conexión a MongoDB cerrada")
	}
	return nil
}

// GetCollection obtiene una colección de MongoDB
func GetCollection(collectionName string) *mongo.Collection {
	if MongoDB == nil {
		log.Fatal("MongoDB no está conectado")
	}
	return MongoDB.Collection(collectionName)
}
