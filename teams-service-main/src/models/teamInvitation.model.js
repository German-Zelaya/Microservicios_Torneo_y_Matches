import { DataTypes } from "sequelize";
import sequelize from "../config/db.js";

const TeamInvitation = sequelize.define("TeamInvitation", {
  id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },

  teamId: { type: DataTypes.UUID, allowNull: false },
  userId: { type: DataTypes.UUID, allowNull: false },

  token: { type: DataTypes.STRING, allowNull: false },

  status: {
    type: DataTypes.ENUM("PENDING", "ACCEPTED", "REJECTED"),
    defaultValue: "PENDING",
  },
});

export default TeamInvitation;
