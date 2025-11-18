import express from "express";
import authRoutes from "./routes/auth.routes.js";
import userRoutes from "./routes/user.routes.js";
import { setupSwagger } from "./config/swagger.js";

const app = express();

app.use(express.json());

// Documentación Swagger
setupSwagger(app);

app.use("/api/auth", authRoutes);
app.use("/api/users", userRoutes);

app.get("/", (req, res) => {
  res.send("Auth Service funcionando 🚀");
});

export default app;
