import { DataTypes } from 'sequelize';
import sequelize from '../config/db.js';

const Team = sequelize.define('Team', {
  id: { type: DataTypes.UUID, primaryKey: true },
  name: { type: DataTypes.STRING, allowNull: false },
  description: { type: DataTypes.TEXT },
  captainId: { type: DataTypes.UUID, allowNull: false },
});

export default Team;
