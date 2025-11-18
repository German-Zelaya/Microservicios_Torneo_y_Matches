import express from 'express';
import { registerTeamToTournament } from '../controllers/teamTournamentController.js';

const router = express.Router();

/**
 * @swagger
 * /api/teams/{id}/tournaments/{tournamentId}/register:
 *   post:
 *     summary: Inscribir un equipo a un torneo
 *     tags:
 *       - Teams
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: ID del equipo
 *       - in: path
 *         name: tournamentId
 *         schema:
 *           type: string
 *         required: true
 *         description: ID del torneo
 *     requestBody:
 *       description: Información opcional adicional para el registro
 *       required: false
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               extraInfo:
 *                 type: string
 *                 example: "Notas adicionales sobre la inscripción"
 *     responses:
 *       200:
 *         description: Registro exitoso
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: "Equipo inscrito exitosamente"
 *                 registration:
 *                   type: object
 *       400:
 *         description: Error en los datos enviados
 *       404:
 *         description: Equipo o torneo no encontrado
 *       500:
 *         description: Error interno del servidor
 */
router.post('/:id/tournaments/:tournamentId/register', registerTeamToTournament);

export default router;
