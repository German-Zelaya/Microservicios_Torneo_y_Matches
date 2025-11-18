import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import jwt from "jsonwebtoken";
import User from "./models/user.model.js"; // Sequelize User
import { Op } from "sequelize";

const PROTO_PATH = "./proto/user.proto";

// Cargar proto
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const proto = grpc.loadPackageDefinition(packageDefinition).userservice;

// Implementación de métodos
const userServiceImpl = {
  ValidateToken: async (call, callback) => {
    try {
      const { token } = call.request;
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findByPk(decoded.id);
      if (!user) return callback(null, {}); // Devuelve vacío si no existe

      callback(null, {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
      });
    } catch (err) {
      callback({
        code: grpc.status.UNAUTHENTICATED,
        message: "Token inválido",
      });
    }
  },

  GetUserById: async (call, callback) => {
    const { id } = call.request;
    const user = await User.findByPk(id);
    if (!user) return callback({ code: grpc.status.NOT_FOUND, message: "Usuario no encontrado" });

    callback(null, {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
    });
  },

  GetUsersByIds: async (call, callback) => {
    const { ids } = call.request;
    const users = await User.findAll({ where: { id: { [Op.in]: ids } } });
    const usersResponse = users.map(u => ({
      id: u.id,
      username: u.username,
      email: u.email,
      role: u.role,
    }));
    callback(null, { users: usersResponse });
  },

  CheckPermission: async (call, callback) => {
    const { userId, action } = call.request;
    const user = await User.findByPk(userId);
    if (!user) return callback({ code: grpc.status.NOT_FOUND, message: "Usuario no encontrado" });

    // Ejemplo simple: solo admin puede crear torneos
    let allowed = false;
    if (action === "create_tournament" && user.role === "admin") allowed = true;
    if (action === "view_results") allowed = true; // todos pueden ver resultados

    callback(null, { allowed });
  },
};

// Crear servidor
const server = new grpc.Server();
server.addService(proto.UserService.service, userServiceImpl);

const PORT = "0.0.0.0:50051";
server.bindAsync(PORT, grpc.ServerCredentials.createInsecure(), () => {
  console.log(`gRPC UserService corriendo en ${PORT}`);
  server.start();
});
