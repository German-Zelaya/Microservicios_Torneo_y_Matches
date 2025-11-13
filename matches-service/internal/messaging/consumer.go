package messaging

import (
	"encoding/json"
	"fmt"
	"log"

	amqp "github.com/rabbitmq/amqp091-go"

	"matches-service/config"
)

var (
	ConsumerConn    *amqp.Connection
	ConsumerChannel *amqp.Channel
)

// ConnectConsumer conecta al servidor RabbitMQ como consumidor
func ConnectConsumer(cfg *config.Config) error {
	var err error

	// Conectar
	ConsumerConn, err = amqp.Dial(cfg.GetRabbitMQURL())
	if err != nil {
		return fmt.Errorf("error al conectar a RabbitMQ: %w", err)
	}

	// Crear canal
	ConsumerChannel, err = ConsumerConn.Channel()
	if err != nil {
		return fmt.Errorf("error al crear canal: %w", err)
	}

	// Declarar exchange (asegurar que existe)
	err = ConsumerChannel.ExchangeDeclare(
		ExchangeName,
		"topic",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("error al declarar exchange: %w", err)
	}

	log.Println("✅ Conectado a RabbitMQ (Consumer)")

	return nil
}

// CloseConsumer cierra la conexión del consumidor
func CloseConsumer() error {
	if ConsumerChannel != nil {
		ConsumerChannel.Close()
	}
	if ConsumerConn != nil {
		return ConsumerConn.Close()
	}
	return nil
}

// StartConsuming inicia el consumo de eventos de torneos
func StartConsuming() error {
	// Declarar cola exclusiva para este servicio
	queue, err := ConsumerChannel.QueueDeclare(
		"matches_service_queue", // nombre
		true,                    // durable
		false,                   // auto-delete
		false,                   // exclusive
		false,                   // no-wait
		nil,                     // arguments
	)
	if err != nil {
		return fmt.Errorf("error al declarar cola: %w", err)
	}

	// Bindear a eventos de torneos
	routingKeys := []string{
		"tournament.created",
		"tournament.updated",
		"tournament.deleted",
		"tournament.status.*",
	}

	for _, key := range routingKeys {
		err := ConsumerChannel.QueueBind(
			queue.Name,
			key,
			ExchangeName,
			false,
			nil,
		)
		if err != nil {
			return fmt.Errorf("error al bindear cola: %w", err)
		}
		log.Printf("🎧 Escuchando eventos: %s", key)
	}

	// Configurar QoS
	err = ConsumerChannel.Qos(
		1,     // prefetch count
		0,     // prefetch size
		false, // global
	)
	if err != nil {
		return fmt.Errorf("error al configurar QoS: %w", err)
	}

	// Consumir mensajes
	msgs, err := ConsumerChannel.Consume(
		queue.Name,
		"matches-service-consumer",
		false, // auto-ack (false para ack manual)
		false, // exclusive
		false, // no-local
		false, // no-wait
		nil,   // args
	)
	if err != nil {
		return fmt.Errorf("error al iniciar consumidor: %w", err)
	}

	// Procesar mensajes en goroutine
	go func() {
		for msg := range msgs {
			if err := handleMessage(msg); err != nil {
				log.Printf("❌ Error al procesar mensaje: %v", err)
				msg.Nack(false, true) // Requeue el mensaje
			} else {
				msg.Ack(false) // Confirmar procesamiento
			}
		}
	}()

	log.Println("👂 Consumer iniciado, esperando eventos...")

	return nil
}

// handleMessage procesa un mensaje recibido
func handleMessage(msg amqp.Delivery) error {
	var event Event
	if err := json.Unmarshal(msg.Body, &event); err != nil {
		return fmt.Errorf("error al deserializar evento: %w", err)
	}

	log.Printf("📩 Evento recibido: %s (routing: %s)", event.EventType, event.RoutingKey)

	// Procesar según el tipo de evento
	switch event.EventType {
	case "TOURNAMENT_CREATED":
		return handleTournamentCreated(event.Data)
	case "TOURNAMENT_UPDATED":
		return handleTournamentUpdated(event.Data)
	case "TOURNAMENT_DELETED":
		return handleTournamentDeleted(event.Data)
	case "TOURNAMENT_STATUS_CHANGED":
		return handleTournamentStatusChanged(event.Data)
	default:
		log.Printf("⚠️ Tipo de evento desconocido: %s", event.EventType)
	}

	return nil
}

// handleTournamentCreated maneja la creación de un torneo
func handleTournamentCreated(data map[string]interface{}) error {
	tournamentID := data["id"]
	tournamentName := data["name"]

	log.Printf("🆕 Torneo creado: ID=%v, Name=%s", tournamentID, tournamentName)

	// Aquí podrías:
	// - Crear estructura de partidas automáticamente
	// - Inicializar brackets
	// - Preparar estadísticas en MongoDB

	return nil
}

// handleTournamentUpdated maneja la actualización de un torneo
func handleTournamentUpdated(data map[string]interface{}) error {
	tournamentID := data["id"]

	log.Printf("✏️ Torneo actualizado: ID=%v", tournamentID)

	// Aquí podrías:
	// - Actualizar datos relacionados en las partidas
	// - Sincronizar información

	return nil
}

// handleTournamentDeleted maneja la eliminación de un torneo
func handleTournamentDeleted(data map[string]interface{}) error {
	tournamentID := data["tournament_id"]

	log.Printf("🗑️ Torneo eliminado: ID=%v", tournamentID)

	// Aquí podrías:
	// - Cancelar todas las partidas asociadas
	// - Limpiar datos

	return nil
}

// handleTournamentStatusChanged maneja cambios de estado de torneo
func handleTournamentStatusChanged(data map[string]interface{}) error {
	tournamentID := data["id"]
	newStatus := data["new_status"]
	oldStatus := data["old_status"]

	log.Printf("🔄 Estado de torneo cambió: ID=%v, %s → %s", tournamentID, oldStatus, newStatus)

	// Aquí podrías:
	// - Si cambió a "in_progress": generar brackets automáticamente
	// - Si cambió a "completed": finalizar todas las partidas
	// - Si cambió a "registration": abrir inscripciones

	if newStatus == "in_progress" {
		log.Printf("🎮 Torneo iniciado, generar brackets para torneo ID=%v", tournamentID)
		// TODO: Implementar generación de brackets
	}

	return nil
}
