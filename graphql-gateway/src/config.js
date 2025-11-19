require('dotenv').config();

module.exports = {
  port: process.env.PORT || 4000,
  nodeEnv: process.env.NODE_ENV || 'development',
  services: {
    tournaments: process.env.TOURNAMENTS_SERVICE_URL || 'http://localhost:8001',
    matches: process.env.MATCHES_SERVICE_URL || 'http://localhost:8002',
    auth: process.env.AUTH_SERVICE_URL || 'http://localhost:3000',
    teams: process.env.TEAMS_SERVICE_URL || 'http://localhost:3002'
  }
};
