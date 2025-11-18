import app from './app.js';
import sequelize from './config/db.js';
import { connectRabbitMQ } from "./config/RabbitMQ.js";
import { startGrpcServer } from "./grpcServer.js";
import { consumeTournamentCreated } from "./consumers/tournamentConsumer.js";

const PORT = process.env.PORT || 3002;

async function startServer() {
  try {
    // 1. Conectar a la base de datos
    await sequelize.sync({ alter: true });
    console.log('✅ Conectado a la base de datos');

    // 2. Conectar a RabbitMQ
    await connectRabbitMQ();
    console.log('🐇 RabbitMQ conectado');

    // 3. Iniciar servidor gRPC
    startGrpcServer();

    // 4. Iniciar consumidor de eventos de torneo
    consumeTournamentCreated();
    console.log('🎧 Consumidor de eventos de torneo iniciado');

    // 5. Iniciar servidor HTTP
    app.listen(PORT, () => {
      console.log(`🚀 Teams Service corriendo en puerto ${PORT}`);
      console.log('📚 Documentación disponible en /api/docs');
    });

  } catch (error) {
    console.error('❌ Error al iniciar Teams Service', error);
    process.exit(1);
  }
}

startServer();
