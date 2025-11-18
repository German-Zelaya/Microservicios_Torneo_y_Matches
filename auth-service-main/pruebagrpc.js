import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";

// Ruta a tu archivo proto
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

// Crear cliente gRPC
const client = new proto.UserService(
  "localhost:50051", // Puerto gRPC
  grpc.credentials.createInsecure()
);

// JWT de un usuario existente para pruebas
const testToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVjYmNmZGM5LTA5MzktNGZhMy04NWNiLWQ2NjJlODA2M2I3YSIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc2MzQ2OTQzNiwiZXhwIjoxNzYzNDc2NjM2fQ.31r1tLu3ydNXGFC0HBImA5pJXP7MxNxfFUvCYGgJ8cg";

// IDs de usuario existentes en la base de datos
const testUserId = "68b2ec37-132e-4d71-afa4-98948db754a2";
const testUserIds = ["68b2ec37-132e-4d71-afa4-98948db754a2", "dfccc50b-765f-4e1a-bf82-96237bf2f787"];

// 1️⃣ Validar token
client.ValidateToken({ token: testToken }, (err, res) => {
  if (err) console.error("ValidateToken error:", err);
  else console.log("ValidateToken result:", res);
});

// 2️⃣ Obtener usuario por ID
client.GetUserById({ id: testUserId }, (err, res) => {
  if (err) console.error("GetUserById error:", err);
  else console.log("GetUserById result:", res);
});

// 3️⃣ Obtener varios usuarios por IDs
client.GetUsersByIds({ ids: testUserIds }, (err, res) => {
  if (err) console.error("GetUsersByIds error:", err);
  else console.log("GetUsersByIds result:", res);
});

// 4️⃣ Comprobar permisos
client.CheckPermission({ userId: testUserId, action: "create_tournament" }, (err, res) => {
  if (err) console.error("CheckPermission error:", err);
  else console.log("CheckPermission result:", res.allowed);
});
