const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');
const { ApolloServerPluginDrainHttpServer } = require('@apollo/server/plugin/drainHttpServer');
const express = require('express');
const http = require('http');
const cors = require('cors');
const config = require('./config');
const typeDefs = require('./schema');
const resolvers = require('./resolvers');

async function startApolloServer() {
  const app = express();
  const httpServer = http.createServer(app);

  // Crear instancia de Apollo Server
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    plugins: [ApolloServerPluginDrainHttpServer({ httpServer })],
    formatError: (formattedError, error) => {
      console.error('GraphQL Error:', error);
      return {
        message: formattedError.message,
        locations: formattedError.locations,
        path: formattedError.path,
        extensions: {
          code: formattedError.extensions?.code || 'INTERNAL_SERVER_ERROR',
        },
      };
    },
  });

  // Iniciar Apollo Server
  await server.start();

  // Aplicar middlewares
  app.use(
    '/graphql',
    cors(),
    express.json(),
    expressMiddleware(server, {
      context: async ({ req }) => ({
        // Aquí puedes agregar contexto, como autenticación
        token: req.headers.authorization || '',
      }),
    })
  );

  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      service: 'GraphQL Gateway',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
    });
  });

  // Root endpoint
  app.get('/', (req, res) => {
    res.json({
      message: 'GraphQL API Gateway for Tournaments and Matches',
      graphql: '/graphql',
      health: '/health',
    });
  });

  // Iniciar servidor
  await new Promise((resolve) => httpServer.listen({ port: config.port }, resolve));

  console.log('\n🚀 GraphQL Gateway iniciado correctamente!\n');
  console.log(`📍 GraphQL Playground: http://localhost:${config.port}/graphql`);
  console.log(`🏥 Health Check: http://localhost:${config.port}/health`);
  console.log('\n📡 Servicios conectados:');
  console.log(`   - Tournaments: ${config.services.tournaments}`);
  console.log(`   - Matches: ${config.services.matches}`);
  console.log(`   - Auth: ${config.services.auth}`);
  console.log(`   - Teams: ${config.services.teams}`);
  console.log('\n✨ Listo para recibir consultas GraphQL!\n');
}

// Manejar errores no capturados
process.on('unhandledRejection', (error) => {
  console.error('❌ Unhandled Rejection:', error);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

// Iniciar el servidor
startApolloServer().catch((error) => {
  console.error('❌ Error al iniciar el servidor:', error);
  process.exit(1);
});
