import Team from "./team.model.js";
import TeamMember from "./teamMember.model.js";
import TeamInvitation from "./teamInvitation.model.js";
import TeamTournament from "./TeamTournament.js";

// Relaciones
Team.hasMany(TeamMember, { as: "members", foreignKey: "teamId" });
TeamMember.belongsTo(Team, { foreignKey: "teamId" });

export {
  Team,
  TeamMember,
  TeamInvitation,
  TeamTournament,
};
