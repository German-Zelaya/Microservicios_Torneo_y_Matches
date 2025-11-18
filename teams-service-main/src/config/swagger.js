import swaggerUi from "swagger-ui-express";
import swaggerJsdoc from "swagger-jsdoc";

export function setupSwagger(app) {
  const options = {
    definition: {
      openapi: "3.0.0",
      info: {
        title: "Teams Service API",
        version: "1.0.0",
        description: "API para gestionar equipos, membresía e inscripciones",
      },
      servers: [
        {
          url: `http://localhost:${process.env.PORT || 3002}`,
        },
      ],
    },
    apis: ["./src/routes/*.js"], // ruta donde están tus rutas con JSDoc
  };

  const specs = swaggerJsdoc(options);
  app.use("/api/docs", swaggerUi.serve, swaggerUi.setup(specs));
}
