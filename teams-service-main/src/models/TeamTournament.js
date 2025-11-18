// src/models/TeamTournament.js
import { DataTypes } from "sequelize";
import sequelize from "../config/db.js";

const TeamTournament = sequelize.define("team_tournaments", {
  id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
  teamId: { type: DataTypes.UUID, allowNull: false },
  tournamentId: { type: DataTypes.UUID, allowNull: false },
});

export default TeamTournament;
