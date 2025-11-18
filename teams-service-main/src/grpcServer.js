// teams-service/src/grpcServer.js

import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import { Team, TeamMember } from "./models/index.js";
import path from "path"; // <-- Usar 'import' para path
import { fileURLToPath } from 'url'; // <-- Necesario para __dirname

// Definir __dirname de forma compatible con ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// La ruta es relativa al archivo actual (src/grpc)
const PROTO_PATH = path.join(__dirname, 'proto', 'team.proto');

console.log(`__dirname: ${__dirname}`);
console.log(`PROTO_PATH generado del grpcServer: ${PROTO_PATH}`);

// Cargar proto
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const proto = grpc.loadPackageDefinition(packageDefinition).teamservice;

// Implementación
const teamServiceImpl = {
  GetTeamById: async (call, callback) => {
    try {
      const team = await Team.findByPk(call.request.id);
      if (!team) return callback({ code: grpc.status.NOT_FOUND, message: "Equipo no encontrado" });

      callback(null, { id: team.id, name: team.name, ownerId: team.ownerId });
    } catch (err) {
      callback({ code: grpc.status.INTERNAL, message: err.message });
    }
  },

  GetTeamMembers: async (call, callback) => {
    try {
      const team = await Team.findByPk(call.request.id, { include: "members" });
      if (!team) return callback({ code: grpc.status.NOT_FOUND, message: "Equipo no encontrado" });

      const members = team.members.map((m) => ({
        id: m.id,
        username: m.username,
        email: m.email,
        role: m.TeamMember.role,
      }));

      callback(null, { members });
    } catch (err) {
      callback({ code: grpc.status.INTERNAL, message: err.message });
    }
  },

  GetTeamsByIds: async (call, callback) => {
    try {
      const teams = await Team.findAll({ where: { id: call.request.ids } });
      const teamsResponse = teams.map((t) => ({
        id: t.id,
        name: t.name,
        ownerId: t.ownerId,
      }));
      callback(null, { teams: teamsResponse });
    } catch (err) {
      callback({ code: grpc.status.INTERNAL, message: err.message });
    }
  },

  ValidateTeamEligibility: async (call, callback) => {
    try {
      const { teamId, tournamentId } = call.request;

      // Ejemplo simple: validar que equipo tenga >=1 miembros
      const team = await Team.findByPk(teamId, { include: "members" });
      const eligible = team && team.members.length > 0;

      callback(null, { eligible });
    } catch (err) {
      callback({ code: grpc.status.INTERNAL, message: err.message });
    }
  },
};

// Crear servidor gRPC
export const startGrpcServer = () => {
  const server = new grpc.Server();
  server.addService(proto.TeamService.service, teamServiceImpl);

  const PORT = "0.0.0.0:50052";
  server.bindAsync(PORT, grpc.ServerCredentials.createInsecure(), () => {
    console.log(`gRPC TeamService corriendo en ${PORT}`);
    server.start();
  });
};
