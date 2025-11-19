const gql = require('graphql-tag');

const typeDefs = gql`
  # ========================================
  # ENUMS
  # ========================================
  
  enum TournamentStatus {
    pending
    registration
    in_progress
    completed
    cancelled
  }

  enum TournamentType {
    individual
    team
  }

  enum MatchStatus {
    scheduled
    in_progress
    completed
    cancelled
  }

  # ========================================
  # TYPES - TOURNAMENTS
  # ========================================
  
  type Tournament {
    id: Int!
    name: String!
    game: String!
    description: String
    max_participants: Int!
    current_participants: Int!
    status: TournamentStatus!
    tournament_type: TournamentType!
    registration_start: String
    registration_end: String
    tournament_start: String
    tournament_end: String
    created_at: String!
    updated_at: String!
    matches: [Match!]
  }

  type TournamentListResponse {
    tournaments: [Tournament!]!
    total: Int!
    page: Int!
    page_size: Int!
    total_pages: Int!
  }

  type BracketMatch {
    match_id: String!
    round: Int!
    position: Int!
    player1_id: String
    player2_id: String
    winner_id: String
    next_match_id: String
  }

  type BracketInfo {
    tournament_id: Int!
    total_rounds: Int!
    total_matches: Int!
    matches: [BracketMatch!]!
  }

  # ========================================
  # TYPES - MATCHES
  # ========================================
  
  type Match {
    id: String!
    tournament_id: Int!
    round: Int!
    position: Int!
    player1_id: String
    player2_id: String
    winner_id: String
    status: MatchStatus!
    scheduled_time: String
    start_time: String
    end_time: String
    created_at: String!
    updated_at: String!
    tournament: Tournament
    result: Result
  }

  type Result {
    id: String!
    match_id: String!
    player1_score: Int
    player2_score: Int
    reporter_id: String!
    validated: Boolean!
    validated_by: String
    validated_at: String
    notes: String
    created_at: String!
    updated_at: String!
  }

  type MatchListResponse {
    matches: [Match!]!
    total: Int!
  }

  # ========================================
  # INPUTS - TOURNAMENTS
  # ========================================
  
  input CreateTournamentInput {
    name: String!
    game: String!
    description: String
    max_participants: Int
    tournament_type: TournamentType
    registration_start: String
    registration_end: String
    tournament_start: String
    tournament_end: String
  }

  input UpdateTournamentInput {
    name: String
    game: String
    description: String
    max_participants: Int
    registration_start: String
    registration_end: String
    tournament_start: String
    tournament_end: String
  }

  input StartTournamentInput {
    participant_ids: [String!]!
  }

  # ========================================
  # INPUTS - MATCHES
  # ========================================
  
  input CreateMatchInput {
    tournament_id: Int!
    round: Int!
    position: Int!
    player1_id: String
    player2_id: String
    scheduled_time: String
  }

  input UpdateMatchInput {
    player1_id: String
    player2_id: String
    winner_id: String
    scheduled_time: String
  }

  input ReportResultInput {
    player1_score: Int!
    player2_score: Int!
    reporter_id: String!
    notes: String
  }

  # ========================================
  # QUERIES
  # ========================================
  
  type Query {
    # Tournaments
    tournaments(
      page: Int
      page_size: Int
      game: String
      status: TournamentStatus
    ): TournamentListResponse!
    
    tournament(id: Int!): Tournament!
    
    # Matches
    matches(
      tournament_id: Int
      status: MatchStatus
      round: Int
    ): MatchListResponse!
    
    match(id: String!): Match!
    
    # Health checks
    health: String!
    healthTournaments: String!
    healthMatches: String!
  }

  # ========================================
  # MUTATIONS
  # ========================================
  
  type Mutation {
    # Tournaments
    createTournament(input: CreateTournamentInput!): Tournament!
    
    updateTournament(id: Int!, input: UpdateTournamentInput!): Tournament!
    
    deleteTournament(id: Int!): Boolean!
    
    changeTournamentStatus(id: Int!, status: TournamentStatus!): Tournament!
    
    startTournament(id: Int!, input: StartTournamentInput!): BracketInfo!
    
    # Matches
    createMatch(input: CreateMatchInput!): Match!
    
    updateMatch(id: String!, input: UpdateMatchInput!): Match!
    
    deleteMatch(id: String!): Boolean!
    
    startMatch(id: String!): Match!
    
    completeMatch(id: String!): Match!
    
    cancelMatch(id: String!): Match!
    
    reportResult(id: String!, input: ReportResultInput!): Result!
    
    validateResult(id: String!): Result!
  }
`;

module.exports = typeDefs;
