import TeamTournament from "../models/TeamTournament.js";
import Team from "../models/team.model.js";
import { client as tournamentClient } from "../grpc/tournamentsClient.js";
import { publishEvent } from "../config/RabbitMQ.js";
import { promisify } from "util";

// Promisificar la llamada gRPC
const validateEligibility = promisify(tournamentClient.ValidateTeamEligibility.bind(tournamentClient));

export const registerTeamToTournament = async (req, res) => {
  const { id: teamId, tournamentId } = req.params;

  try {
    // 1. Verificar que el equipo exista y tenga miembros
    const team = await Team.findByPk(teamId, { include: "members" });
    if (!team) return res.status(404).json({ error: "Equipo no encontrado" });
    if (!team.members || team.members.length === 0)
      return res.status(400).json({ error: "Equipo no tiene miembros" });

    // 2. Validar torneo en Tournaments Service via gRPC
    const response = await validateEligibility({ teamId, tournamentId });

    if (!response.eligible)
      return res.status(403).json({ error: "Equipo no elegible para torneo" });

    // 3. Registrar inscripción en la DB local
    const registration = await TeamTournament.create({ teamId, tournamentId });

    // 4. Emitir evento team.registered
    await publishEvent("team.registered", {
      teamId,
      tournamentId,
      teamName: team.name,
      tournamentName: response.tournamentName || "Nombre del torneo no disponible",
      memberIds: team.members.map(m => m.id),
      timestamp: new Date()
    });

    res.json({ message: "Equipo inscrito exitosamente", registration });

  } catch (error) {
    console.error("registerTeamToTournament error:", error);
    res.status(500).json({ error: "Error al registrar equipo" });
  }
};
