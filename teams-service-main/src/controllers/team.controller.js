import Team from '../models/team.model.js';
import { v4 as uuidv4 } from 'uuid';
import TeamMember from "../models/teamMember.model.js";
import TeamInvitation from "../models/teamInvitation.model.js";
import axios from "axios";
import crypto from "crypto";
import { publishEvent } from "../config/RabbitMQ.js";

// URL del Auth Service
const AUTH_URL = process.env.AUTH_SERVICE_URL + "/api/users";

// ================== CREAR EQUIPO ==================
export const createTeam = async (req, res) => {
  try {
    const { name, captainId } = req.body;

    // Crear equipo con tu estructura actual
    const newTeam = await Team.create({
      id: uuidv4(),
      name,
      captainId
    });

    // Emitir evento team.created
    await publishEvent("team.created", {
      type: "team.created",
      teamId: newTeam.id,
      captainId,
      name,
      timestamp: new Date()
    });

    res.status(201).json(newTeam);
  } catch (error) {
    console.error("❌ Error creando equipo:", error);
    res.status(500).json({ message: "Error creando equipo", error: error.message });
  }
};


// ================== OBTENER EQUIPO POR ID ==================
export const getTeamById = async (req, res) => {
  try {
    const team = await Team.findByPk(req.params.id, {
      include: [{ model: TeamMember, as: 'TeamMembers' }]
    });
    if (!team) return res.status(404).json({ message: 'Equipo no encontrado' });
    res.json(team);
  } catch (error) {
    res.status(500).json({ message: 'Error obteniendo equipo', error: error.message });
  }
};

// ================== ACTUALIZAR EQUIPO ==================
export const updateTeam = async (req, res) => {
  try {
    const { id } = req.params;

    const team = await Team.findByPk(id);
    if (!team) return res.status(404).json({ message: "Equipo no encontrado" });

    await team.update(req.body);

    return res.json({ message: "Equipo actualizado", team });
  } catch (error) {
    console.error("updateTeam error:", error);
    return res.status(500).json({ error: "Error actualizando el equipo" });
  }
};

// ================== ELIMINAR EQUIPO ==================
export const deleteTeam = async (req, res) => {
  try {
    const { id } = req.params;

    const team = await Team.findByPk(id);
    if (!team) return res.status(404).json({ message: "Equipo no encontrado" });

    await TeamMember.destroy({ where: { teamId: id } });
    await team.destroy();

    return res.json({ message: "Equipo eliminado" });
  } catch (error) {
    console.error("deleteTeam error:", error);
    return res.status(500).json({ error: "Error eliminando el equipo" });
  }
};

// ================== OBTENER EQUIPOS DE UN USUARIO ==================
export const getTeamsByUser = async (req, res) => {
  try {
    const { userId } = req.params;

    const teams = await Team.findAll({
      include: [
        {
          model: TeamMember,
          where: { userId },
          required: true,
        },
      ],
    });

    return res.json({ teams });
  } catch (error) {
    console.error("getTeamsByUser error:", error);
    return res.status(500).json({ error: "Error obteniendo equipos del usuario" });
  }
};

// =======================================================
// 1. Invitar miembro
// =======================================================
export const inviteMember = async (req, res) => {
  try {
    const { id } = req.params; // teamId
    const { userId } = req.body;

    const team = await Team.findByPk(id);
    if (!team) {
      return res.status(404).json({ message: "Equipo no existe" });
    }

    // Validar usuario en Auth Service
    const authHeader = req.headers.authorization;
    const userCheck = await axios.get(`${AUTH_URL}/${userId}`, {
      headers: authHeader ? { Authorization: authHeader } : {}
    }).catch(() => null);
    if (!userCheck) {
      return res.status(404).json({ message: "Usuario no existe" });
    }

    // Token único para aceptar invitación
    const token = crypto.randomBytes(20).toString("hex");

    const invitation = await TeamInvitation.create({
      teamId: id,
      userId,
      token,
    });

    // Emitir evento para notificación
    await publishEvent("team.member.invited", {
      type: "team.member.invited",
      teamId: id,
      userId,
      invitedBy: team.captainId,
      teamName: team.name,
      token,
      timestamp: new Date()
    });

    return res.json({
      message: "Invitación enviada",
      invitation
    });

  } catch (error) {
    console.error("inviteMember error:", error);
    res.status(500).json({ error: "Error invitando al usuario" });
  }
};

// =======================================================
// 2. Aceptar invitación
// =======================================================
export const acceptInvitation = async (req, res) => {
  try {
    const { id, token } = req.params;

    const invitation = await TeamInvitation.findOne({
      where: { teamId: id, token, status: "PENDING" },
    });

    if (!invitation)
      return res.status(400).json({ message: "Invitación inválida o expirada" });

    // Agregar al equipo
    await TeamMember.create({
      id: uuidv4(),
      teamId: id,
      userId: invitation.userId,
      role: "MEMBER",
    });

    // Marcar invitación como aceptada
    invitation.status = "ACCEPTED";
    await invitation.save();

    // Emitir evento (Kafka o RabbitMQ)
    console.log("Emitir evento: team.member.added");

    return res.json({ message: "Invitación aceptada" });
  } catch (error) {
    console.error("acceptInvitation error:", error);
    res.status(500).json({ error: "Error aceptando invitación" });
  }
};

// =======================================================
// 3. Expulsar miembro
// =======================================================
export const removeMember = async (req, res) => {
  try {
    const { id, userId } = req.params;

    const member = await TeamMember.findOne({ where: { teamId: id, userId } });

    if (!member) return res.status(404).json({ message: "Miembro no encontrado" });

    await member.destroy();

    return res.json({ message: "Miembro expulsado" });
  } catch (error) {
    console.error("removeMember error:", error);
    res.status(500).json({ error: "Error expulsando miembro" });
  }
};

// =======================================================
// 4. Cambiar rol
// =======================================================
export const changeMemberRole = async (req, res) => {
  try {
    const { id, userId } = req.params;
    const { role } = req.body;

    const member = await TeamMember.findOne({ where: { teamId: id, userId } });

    if (!member) return res.status(404).json({ message: "Miembro no encontrado" });

    member.role = role;
    await member.save();

    return res.json({ message: "Rol actualizado" });
  } catch (error) {
    console.error("changeMemberRole error:", error);
    res.status(500).json({ error: "Error cambiando rol" });
  }
};

export const registerTeam = async (req, res) => {
  try {
    const { name, ownerId } = req.body;

    const team = await Team.create({ name, ownerId });

    await publishEvent("team.registered", {
      type: "team.registered",
      teamId: team.id,
      ownerId,
      timestamp: new Date()
    });

    res.json(team);
  } catch (err) {
    res.status(500).json({ error: "Error registrando equipo" });
  }
};
