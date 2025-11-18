-- Migration: Change player_id columns from integer to varchar(36) for UUID support
-- Date: 2025-11-18
-- Description: Auth Service uses UUIDs for user IDs, so we need to store them as strings

-- Drop existing indexes if they exist (to allow type change)
DROP INDEX IF EXISTS idx_matches_player1_id;
DROP INDEX IF EXISTS idx_matches_player2_id;
DROP INDEX IF EXISTS idx_matches_winner_id;

-- Change column types to varchar(36) for UUID storage
ALTER TABLE matches
    ALTER COLUMN player1_id TYPE VARCHAR(36),
    ALTER COLUMN player2_id TYPE VARCHAR(36),
    ALTER COLUMN winner_id TYPE VARCHAR(36);

-- Recreate indexes
CREATE INDEX idx_matches_player1_id ON matches(player1_id);
CREATE INDEX idx_matches_player2_id ON matches(player2_id);
CREATE INDEX idx_matches_winner_id ON matches(winner_id);

-- Note: If there's existing data with integer IDs, you may need to handle conversion
-- This migration assumes the table is empty or the data can be converted to strings
