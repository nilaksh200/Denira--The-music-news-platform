-- =============================================================================
-- Denira Desktop — PostgreSQL Database Schema
-- Target: Supabase PostgreSQL (Free Tier)
-- Migration Strategy: Idempotent (safe for initial run & repeated execution)
-- =============================================================================

-- Ensure standard extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- Table: articles
-- Core storage for Inshorts-style desktop music news cards
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    headline TEXT NOT NULL,
    summary TEXT NOT NULL,
    genre VARCHAR(50) NOT NULL,
    source VARCHAR(100) NOT NULL,
    link TEXT NOT NULL,
    image_url TEXT,
    published_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Indexes for High-Performance Desktop Feed Queries
-- -----------------------------------------------------------------------------

-- 1. Primary Chronological Feed Index:
-- Enables rapid reverse-chronological pagination for the default card deck.
CREATE INDEX IF NOT EXISTS idx_articles_published_at_desc 
ON articles (published_at DESC);

-- 2. Genre-Filtered Chronological Index:
-- Supports instant tab/filter switching by genre without seq-scanning the table.
CREATE INDEX IF NOT EXISTS idx_articles_genre_published_at_desc 
ON articles (genre, published_at DESC);

-- 3. Fast Deduplication Lookup Index:
-- Note: url_hash has an implicit unique B-tree index from the UNIQUE constraint.
-- Explicit index creation is omitted to avoid duplicate index storage overhead.

-- -----------------------------------------------------------------------------
-- Table & Column Documentation Comments
-- -----------------------------------------------------------------------------
COMMENT ON TABLE articles IS 'Denira Desktop curated music news cards (100-160 cards per 6h cycle)';
COMMENT ON COLUMN articles.id IS 'Sequential primary key for internal reference and cursor pagination';
COMMENT ON COLUMN articles.url_hash IS 'SHA-256 hash of canonical source article URL for strict deduplication';
COMMENT ON COLUMN articles.headline IS 'Concise, objective card headline (strictly <12 words)';
COMMENT ON COLUMN articles.summary IS 'Synthesized editorial news summary (strictly 50-60 words)';
COMMENT ON COLUMN articles.genre IS 'Primary music genre taxonomy classification (e.g., Electronic, Hip-Hop, Indie)';
COMMENT ON COLUMN articles.source IS 'Human-readable source publication name (e.g., Pitchfork, Resident Advisor)';
COMMENT ON COLUMN articles.link IS 'Canonical outbound destination URL to the original reporting';
COMMENT ON COLUMN articles.image_url IS 'High-resolution artwork or editorial photography URL';
COMMENT ON COLUMN articles.published_at IS 'Original publication timestamp from source feed';
COMMENT ON COLUMN articles.created_at IS 'Ingestion pipeline timestamp when card was synthesized and inserted';
