const tournamentsAPI = require('./datasources/tournaments');
const matchesAPI = require('./datasources/matches');

const resolvers = {
  // ========================================
  // QUERIES
  // ========================================
  Query: {
    // Tournaments
    tournaments: async (_, { page, page_size, game, status }) => {
      return await tournamentsAPI.getTournaments({ page, page_size, game, status });
    },

    tournament: async (_, { id }) => {
      return await tournamentsAPI.getTournament(id);
    },

    // Matches
    matches: async (_, { tournament_id, status, round }) => {
      const matches = await matchesAPI.getMatches({ tournament_id, status, round });
      return {
        matches: Array.isArray(matches) ? matches : [],
        total: Array.isArray(matches) ? matches.length : 0
      };
    },

    match: async (_, { id }) => {
      return await matchesAPI.getMatch(id);
    },

    // Health checks
    health: () => 'GraphQL Gateway is running!',
    
    healthTournaments: async () => {
      try {
        const health = await tournamentsAPI.healthCheck();
        return JSON.stringify(health);
      } catch (error) {
        return error.message;
      }
    },

    healthMatches: async () => {
      try {
        const health = await matchesAPI.healthCheck();
        return JSON.stringify(health);
      } catch (error) {
        return error.message;
      }
    },
  },

  // ========================================
  // MUTATIONS
  // ========================================
  Mutation: {
    // Tournaments
    createTournament: async (_, { input }) => {
      return await tournamentsAPI.createTournament(input);
    },

    updateTournament: async (_, { id, input }) => {
      return await tournamentsAPI.updateTournament(id, input);
    },

    deleteTournament: async (_, { id }) => {
      return await tournamentsAPI.deleteTournament(id);
    },

    changeTournamentStatus: async (_, { id, status }) => {
      return await tournamentsAPI.changeTournamentStatus(id, status);
    },

    startTournament: async (_, { id, input }) => {
      return await tournamentsAPI.startTournament(id, input);
    },

    // Matches
    createMatch: async (_, { input }) => {
      return await matchesAPI.createMatch(input);
    },

    updateMatch: async (_, { id, input }) => {
      return await matchesAPI.updateMatch(id, input);
    },

    deleteMatch: async (_, { id }) => {
      return await matchesAPI.deleteMatch(id);
    },

    startMatch: async (_, { id }) => {
      return await matchesAPI.startMatch(id);
    },

    completeMatch: async (_, { id }) => {
      return await matchesAPI.completeMatch(id);
    },

    cancelMatch: async (_, { id }) => {
      return await matchesAPI.cancelMatch(id);
    },

    reportResult: async (_, { id, input }) => {
      return await matchesAPI.reportResult(id, input);
    },

    validateResult: async (_, { id }) => {
      return await matchesAPI.validateResult(id);
    },
  },

  // ========================================
  // FIELD RESOLVERS
  // ========================================
  Tournament: {
    // Resolver para obtener matches de un torneo
    matches: async (tournament) => {
      try {
        const result = await matchesAPI.getMatches({ tournament_id: tournament.id });
        return Array.isArray(result) ? result : [];
      } catch (error) {
        console.error(`Error fetching matches for tournament ${tournament.id}:`, error.message);
        return [];
      }
    },
  },

  Match: {
    // Resolver para obtener el torneo de un match
    tournament: async (match) => {
      try {
        return await tournamentsAPI.getTournament(match.tournament_id);
      } catch (error) {
        console.error(`Error fetching tournament ${match.tournament_id}:`, error.message);
        return null;
      }
    },

    // Resolver para obtener el resultado de un match
    result: async (match) => {
      // Si el match ya tiene el resultado incluido, retornarlo
      if (match.result) {
        return match.result;
      }
      // Si no, podrías hacer una llamada adicional si el servicio lo soporta
      return null;
    },
  },
};

module.exports = resolvers;
