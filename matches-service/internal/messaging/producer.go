package messaging

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"

	"matches-service/config"
)

var (
	ProducerConn    *amqp.Connection
	ProducerChannel *amqp.Channel
	ExchangeName    = "tournaments_exchange"
)

// ConnectProducer conecta al servidor RabbitMQ como productor
func ConnectProducer(cfg *config.Config) error {
	var err error

	// Conectar
	ProducerConn, err = amqp.Dial(cfg.GetRabbitMQURL())
	if err != nil {
		return fmt.Errorf("error al conectar a RabbitMQ: %w", err)
	}

	// Crear canal
	ProducerChannel, err = ProducerConn.Channel()
	if err != nil {
		return fmt.Errorf("error al crear canal: %w", err)
	}

	// Declarar exchange (mismo que tournaments-service)
	err = ProducerChannel.ExchangeDeclare(
		ExchangeName, // nombre
		"topic",      // tipo
		true,         // durable
		false,        // auto-deleted
		false,        // internal
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		return fmt.Errorf("error al declarar exchange: %w", err)
	}

	log.Printf("✅ Conectado a RabbitMQ (Producer)")
	log.Printf("📢 Exchange '%s' declarado", ExchangeName)

	return nil
}

// CloseProducer cierra la conexión del productor
func CloseProducer() error {
	if ProducerChannel != nil {
		ProducerChannel.Close()
	}
	if ProducerConn != nil {
		return ProducerConn.Close()
	}
	return nil
}

// IsProducerConnected verifica si el productor está conectado
func IsProducerConnected() bool {
	return ProducerConn != nil && !ProducerConn.IsClosed()
}

// Event representa un evento genérico
type Event struct {
	EventType  string                 `json:"event_type"`
	RoutingKey string                 `json:"routing_key"`
	Data       map[string]interface{} `json:"data"`
	Timestamp  time.Time              `json:"timestamp"`
}

// PublishEvent publica un evento en RabbitMQ
func PublishEvent(routingKey, eventType string, data map[string]interface{}) error {
	if !IsProducerConnected() {
		log.Printf("⚠️ RabbitMQ no conectado. Evento no publicado: %s", routingKey)
		return nil // No fallar si RabbitMQ no está disponible
	}

	event := Event{
		EventType:  eventType,
		RoutingKey: routingKey,
		Data:       data,
		Timestamp:  time.Now(),
	}

	body, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("error al serializar evento: %w", err)
	}

	err = ProducerChannel.Publish(
		ExchangeName, // exchange
		routingKey,   // routing key
		false,        // mandatory
		false,        // immediate
		amqp.Publishing{
			ContentType:  "application/json",
			Body:         body,
			DeliveryMode: amqp.Persistent, // Mensaje persistente
			Timestamp:    time.Now(),
		},
	)

	if err != nil {
		return fmt.Errorf("error al publicar evento: %w", err)
	}

	log.Printf("📤 Evento publicado: %s", routingKey)
	return nil
}

// PublishMatchCreated publica evento de partida creada
func PublishMatchCreated(matchData map[string]interface{}) error {
	return PublishEvent("match.created", "MATCH_CREATED", matchData)
}

// PublishMatchStarted publica evento de partida iniciada
func PublishMatchStarted(matchData map[string]interface{}) error {
	return PublishEvent("match.started", "MATCH_STARTED", matchData)
}

// PublishMatchCompleted publica evento de partida completada
func PublishMatchCompleted(matchData map[string]interface{}) error {
	return PublishEvent("match.completed", "MATCH_COMPLETED", matchData)
}

// PublishMatchCancelled publica evento de partida cancelada
func PublishMatchCancelled(matchData map[string]interface{}) error {
	return PublishEvent("match.cancelled", "MATCH_CANCELLED", matchData)
}

// PublishResultRecorded publica evento de resultado registrado
func PublishResultRecorded(resultData map[string]interface{}) error {
	return PublishEvent("match.result.recorded", "RESULT_RECORDED", resultData)
}

// PublishMatchResultReported publica evento de resultado reportado (pendiente validación)
func PublishMatchResultReported(matchData map[string]interface{}) error {
	return PublishEvent("match.result.reported", "MATCH_RESULT_REPORTED", matchData)
}

// PublishMatchFinished publica evento de partida finalizada y validada
func PublishMatchFinished(matchData map[string]interface{}) error {
	return PublishEvent("match.finished", "MATCH_FINISHED", matchData)
}

// PublishMatchResultRejected publica evento de resultado rechazado
func PublishMatchResultRejected(matchData map[string]interface{}) error {
	return PublishEvent("match.result.rejected", "MATCH_RESULT_REJECTED", matchData)
}
