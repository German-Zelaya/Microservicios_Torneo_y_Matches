package messaging

import (
	"encoding/json"
	"fmt"
	"log"

	amqp "github.com/rabbitmq/amqp091-go"

	"matches-service/config"
	"matches-service/internal/database"
	"matches-service/internal/models"
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
		"tournament.bracket.generated", // Nuevo: escuchar generación de brackets
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
	case "BRACKET_GENERATED":
		return handleBracketGenerated(event.Data)
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

// handleBracketGenerated maneja la generación de brackets
func handleBracketGenerated(data map[string]interface{}) error {
	tournamentID := data["tournament_id"]
	tournamentName := data["tournament_name"]
	totalParticipants := data["total_participants"]

	log.Printf("🎯 Bracket generado para torneo: ID=%v, Name=%s, Participantes=%v",
		tournamentID, tournamentName, totalParticipants)

	// Obtener los matches a crear
	matchesData, ok := data["matches"].([]interface{})
	if !ok {
		return fmt.Errorf("formato inválido de matches en bracket")
	}

	log.Printf("📋 Creando %d matches de la primera ronda...", len(matchesData))

	// Crear cada match usando el servicio
	for i, matchInterface := range matchesData {
		matchMap, ok := matchInterface.(map[string]interface{})
		if !ok {
			log.Printf("⚠️ Formato inválido en match %d, saltando...", i)
			continue
		}

		// Convertir tipos
		tournamentIDFloat, _ := tournamentID.(float64)
		roundFloat, _ := matchMap["round"].(float64)
		matchNumberFloat, _ := matchMap["match_number"].(float64)
		player1Float, _ := matchMap["player1_id"].(float64)
		player2Float, _ := matchMap["player2_id"].(float64)

		// Crear match en la base de datos
		err := createMatchFromBracket(
			uint(tournamentIDFloat),
			int(roundFloat),
			int(matchNumberFloat),
			uint(player1Float),
			uint(player2Float),
		)

		if err != nil {
			log.Printf("❌ Error al crear match %d: %v", i+1, err)
			continue
		}

		log.Printf("✅ Match %d creado: Round %d, Match %d",
			i+1, int(roundFloat), int(matchNumberFloat))
	}

	log.Printf("🎉 Bracket generado completamente para torneo ID=%v", tournamentID)
	return nil
}

// handleTournamentStatusChanged maneja el cambio de estado de un torneo
func handleTournamentStatusChanged(data map[string]interface{}) error {
	tournamentID := data["tournament_id"]
	status := data["status"]

	log.Printf("🔄 Estado de torneo cambiado: ID=%v, Status=%s", tournamentID, status)

	// Aquí podrías:
	// - Actualizar el estado de los matches relacionados según el estado del torneo
	// - Si el torneo se cancela, cancelar todos los matches
	// - Si el torneo inicia, activar los matches de la primera ronda
	// - Sincronizar información relevante

	return nil
}

// createMatchFromBracket crea un match desde el bracket generado
func createMatchFromBracket(tournamentID uint, round, matchNumber int, player1ID, player2ID uint) error {
	// Importar modelos y base de datos
	match := &models.Match{
		TournamentID: tournamentID,
		Round:        round,
		MatchNumber:  matchNumber,
		Player1ID:    &player1ID,
		Player2ID:    &player2ID,
		Status:       models.MatchStatusScheduled,
		Player1Score: 0,
		Player2Score: 0,
	}

	if err := database.PostgresDB.Create(match).Error; err != nil {
		return err
	}

	// Publicar evento de match creado
	matchData := map[string]interface{}{
		"id":            match.ID,
		"tournament_id": match.TournamentID,
		"round":         match.Round,
		"match_number":  match.MatchNumber,
		"player1_id":    player1ID,
		"player2_id":    player2ID,
		"status":        string(match.Status),
	}

	PublishMatchCreated(matchData)

	return nil
}
