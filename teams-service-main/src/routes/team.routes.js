/**
 * @swagger
 * tags:
 *   name: Teams
 *   description: Gestión de equipos
 */

import express from 'express';
import {
  createTeam,
  getTeamById,
  updateTeam,
  deleteTeam,
  getTeamsByUser,
} from "../controllers/team.controller.js";

import {
  inviteMember,
  acceptInvitation,
  removeMember,
  changeMemberRole
} from "../controllers/team.controller.js";

const router = express.Router();

/**
 * @swagger
 * /api/teams:
 *   post:
 *     summary: Crear un nuevo equipo
 *     tags: [Teams]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *               - captainId
 *             properties:
 *               name:
 *                 type: string
 *                 example: "Equipo A"
 *               captainId:
 *                 type: string
 *                 format: uuid
 *                 example: "5cbcfdc9-0939-4fa3-85cb-d662e8063b7a"
 *     responses:
 *       201:
 *         description: Equipo creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 teamId:
 *                   type: string
 *                   example: "68b2ec37-132e-4d71-afa4-98948db754a2"
 *                 name:
 *                   type: string
 *                   example: "Equipo A"
 *       400:
 *         description: Error en la solicitud
 */
router.post("/", createTeam);

/**
 * @swagger
 * /api/teams/{id}:
 *   get:
 *     summary: Obtener los detalles de un equipo
 *     tags: [Teams]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *           format: uuid
 *         required: true
 *         description: ID del equipo
 *     responses:
 *       200:
 *         description: Detalles del equipo
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                   example: "68b2ec37-132e-4d71-afa4-98948db754a2"
 *                 name:
 *                   type: string
 *                   example: "Equipo A"
 *                 captainId:
 *                   type: string
 *                   format: uuid
 *                   example: "5cbcfdc9-0939-4fa3-85cb-d662e8063b7a"
 *                 members:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                       username:
 *                         type: string
 *                       role:
 *                         type: string
 *       404:
 *         description: Equipo no encontrado
 */
router.get("/:id", getTeamById);

/**
 * @swagger
 * /api/teams/{id}:
 *   put:
 *     summary: Actualizar equipo
 *     tags: [Teams]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             example:
 *               name: "Nuevo nombre"
 *               description: "Nueva descripción"
 *     responses:
 *       200:
 *         description: Equipo actualizado
 *       404:
 *         description: Equipo no encontrado
 */
router.put("/:id", updateTeam);

/**
 * @swagger
 * /api/teams/{id}:
 *   delete:
 *     summary: Eliminar equipo
 *     tags: [Teams]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Equipo eliminado
 *       404:
 *         description: Equipo no encontrado
 */
router.delete("/:id", deleteTeam);

/**
 * @swagger
 * /api/teams/user/{userId}:
 *   get:
 *     summary: Obtener todos los equipos de un usuario
 *     tags: [Teams]
 *     parameters:
 *       - in: path
 *         name: userId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Lista de equipos del usuario
 */
router.get("/user/:userId", getTeamsByUser);

/**
 * @swagger
 * /api/teams/{id}/invite:
 *   post:
 *     summary: Invitar a un usuario al equipo
 *     tags: [Teams]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             example:
 *               userId: "uuid-del-usuario"
 *     responses:
 *       200:
 *         description: Invitación enviada
 */
router.post("/:id/invite", inviteMember);

/**
 * @swagger
 * /api/teams/{id}/accept/{token}:
 *   post:
 *     summary: Aceptar invitación a equipo
 *     tags: [Teams]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *       - in: path
 *         name: token
 *         required: true
 *     responses:
 *       200:
 *         description: Usuario añadido al equipo
 */
router.post("/:id/accept/:token", acceptInvitation);

/**
 * @swagger
 * /api/teams/{id}/members/{userId}:
 *   delete:
 *     summary: Expulsar miembro del equipo
 *     tags: [Teams]
 */
router.delete("/:id/members/:userId", removeMember);

/**
 * @swagger
 * /api/teams/{id}/members/{userId}/role:
 *   put:
 *     summary: Cambiar rol interno de un miembro
 *     tags: [Teams]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             example:
 *               role: "CAPTAIN"
 */
router.put("/:id/members/:userId/role", changeMemberRole);

export default router;
