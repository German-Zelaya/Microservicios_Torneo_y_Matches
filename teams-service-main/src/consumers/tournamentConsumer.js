// src/consumers/tournamentConsumer.js

import amqp from "amqplib";
import dotenv from "dotenv";
import { Team, TeamMember } from "../models/index.js";

dotenv.config();

const RABBITMQ_URL = process.env.RABBITMQ_URL || "amqp://localhost";

export const consumeTournamentCreated = async () => {
  try {
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();

    const EXCHANGE = "tournament.events";
    const QUEUE = "teams_service_tournament_created";
    const ROUTING_KEY = "tournament.created";

    await channel.assertExchange(EXCHANGE, "topic", { durable: true });
    await channel.assertQueue(QUEUE, { durable: true });
    await channel.bindQueue(QUEUE, EXCHANGE, ROUTING_KEY);

    console.log(`[Teams Service] Esperando eventos de torneo...`);

    channel.consume(
      QUEUE,
      async (msg) => {
        if (msg) {
          const content = JSON.parse(msg.content.toString());
          const { tournamentId, tournamentName } = content;

          console.log(`[Teams Service] Nuevo torneo creado: ${tournamentName} (${tournamentId})`);

          // Aquí puedes definir tu lógica de elegibilidad:
          // Por ejemplo, obtener todos los equipos con al menos 1 miembro
          const eligibleTeams = await Team.findAll({
            include: "members",
          });

          const teamsList = eligibleTeams
            .filter((team) => team.members.length > 0)
            .map((team) => ({
              id: team.id,
              name: team.name,
              members: team.members.map((m) => m.id),
            }));

          console.log(`[Teams Service] Equipos elegibles para el torneo:`, teamsList);

          // Confirmar el mensaje
          channel.ack(msg);
        }
      },
      { noAck: false }
    );
  } catch (error) {
    console.error("Error al consumir torneo creado:", error);
  }
};
