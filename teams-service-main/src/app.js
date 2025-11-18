import express from 'express';
import cors from 'cors';
import teamRoutes from './routes/team.routes.js';
import dotenv from 'dotenv';
import { setupSwagger } from "./config/swagger.js";
import teamTournamentRoutes from "./routes/teamTournamentRoutes.js";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Documentación Swagger
setupSwagger(app);

// Rutas de Teams
app.use('/api/teams', teamRoutes);

// Rutas de registro a torneos
app.use('/api/teams', teamTournamentRoutes);

app.get('/', (req, res) => res.send('Teams Service funcionando 🚀'));

export default app;
