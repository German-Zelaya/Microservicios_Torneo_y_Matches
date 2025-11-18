// teams-service/src/grpc/tournamentsClient.js

import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import dotenv from "dotenv";
import path from "path"; // <-- Añadir importación de path
import { fileURLToPath } from 'url'; // Necesario para obtener __dirname en ES Modules

dotenv.config();

// Definir __dirname de forma compatible con ES Modules (ya que usas 'import')
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// La ruta es relativa al archivo actual (src/grpc).
// Retrocedemos un nivel (..) para alcanzar el directorio src/.
const PROTO_PATH = path.join(__dirname, '..', 'proto', 'team.proto');

// =================== DEBUG START ===================
console.log(`[tournamentsClient] __dirname: ${__dirname}`);
console.log(`[tournamentsClient] PROTO_PATH generado: ${PROTO_PATH}`);
// =================== DEBUG END =====================

const packageDef = protoLoader.loadSync(
  PROTO_PATH, // <-- ¡USAR LA RUTA GENERADA!
  {}
);

const grpcObj = grpc.loadPackageDefinition(packageDef);
const teamPackage = grpcObj.teamservice;

export const client = new teamPackage.TeamService(
  process.env.TOURNAMENTS_SERVICE_GRPC_URL,
  grpc.credentials.createInsecure()
);