import { DataTypes } from 'sequelize';
import sequelize from '../config/db.js';
import Team from './team.model.js';

const TeamMember = sequelize.define('TeamMember', {
  id: { type: DataTypes.UUID, primaryKey: true },
  teamId: { type: DataTypes.UUID, references: { model: Team, key: 'id' } },
  userId: { type: DataTypes.UUID, allowNull: false },
  role: { type: DataTypes.ENUM('CAPTAIN', 'MEMBER'), defaultValue: 'MEMBER' },
});

Team.hasMany(TeamMember, { foreignKey: 'teamId' });
TeamMember.belongsTo(Team, { foreignKey: 'teamId' });

export default TeamMember;
