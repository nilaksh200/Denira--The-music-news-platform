"""
Denira Desktop — Supabase PostgreSQL Database Client
Manages pooled connections, duplicate filtering via url_hash, and bulk card upserts.
Supports graceful mock/fallback mode for zero-setup local development and testing.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("denira.database")


class DatabaseClient:
    """
    PostgreSQL client tailored for Supabase Transaction Pooler (port 6543).
    Ensures safe, idempotent bulk upserts with conflict handling.
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        raw_url = database_url or os.getenv("DATABASE_URL", "").strip()
        self.is_mock = (
            not raw_url
            or "your-ref" in raw_url
            or "your-password" in raw_url
            or raw_url.startswith("postgresql://postgres.your-")
        )
        self.database_url = raw_url

        # In-memory storage for mock/fallback mode
        self._mock_hashes: Set[str] = set()
        self._mock_records: List[Dict[str, Any]] = []

        if self.is_mock:
            logger.info(
                "DATABASE_URL is not configured or contains placeholder credentials. "
                "DatabaseClient running in local in-memory fallback mock mode."
            )
        else:
            logger.info("DatabaseClient initialized with remote PostgreSQL connection string.")

    def _get_connection(self):
        """Creates a PostgreSQL connection with explicit connection timeout."""
        return psycopg2.connect(self.database_url, connect_timeout=10)

    def get_existing_hashes(self, hours_lookback: int = 48) -> Set[str]:
        """
        Retrieves all url_hash keys stored in the database within the lookback window.
        Used to pre-filter harvested candidates before invoking LLM summarization.
        """
        if self.is_mock:
            logger.info(
                "[Mock DB] Queried existing hashes (lookback %dh): %d hashes cached.",
                hours_lookback,
                len(self._mock_hashes),
            )
            return set(self._mock_hashes)

        query = """
            SELECT url_hash 
            FROM articles 
            WHERE created_at > NOW() - (%s || ' hours')::interval;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (hours_lookback,))
                    rows = cur.fetchall()
                    existing = {r[0] for r in rows if r[0]}
                    logger.info(
                        "Fetched %d existing article hashes from database (lookback: %dh).",
                        len(existing),
                        hours_lookback,
                    )
                    return existing
        except Exception as e:
            logger.error(
                "Failed to query existing hashes from database: %s. Falling back to empty set.",
                e,
            )
            return set()

    def upsert_articles(self, cards: List[Dict[str, Any]]) -> int:
        """
        Bulk upserts synthesized editorial cards into the articles table.
        Uses ON CONFLICT (url_hash) DO NOTHING to ensure strict idempotency.
        Returns the count of successfully persisted cards.
        """
        if not cards:
            logger.info("No articles supplied for upsert.")
            return 0

        if self.is_mock:
            inserted_count = 0
            for card in cards:
                h = card.get("url_hash", "")
                if h not in self._mock_hashes:
                    self._mock_hashes.add(h)
                    self._mock_records.append(
                        {
                            "id": len(self._mock_records) + 1,
                            **card,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    inserted_count += 1
            logger.info(
                "[Mock DB] Successfully committed %d new cards (%d duplicate/seen skipped). Total cached: %d",
                inserted_count,
                len(cards) - inserted_count,
                len(self._mock_records),
            )
            return inserted_count

        upsert_query = """
            INSERT INTO articles (
                url_hash, headline, summary, genre, source, link, image_url, published_at
            ) VALUES (
                %(url_hash)s, %(headline)s, %(summary)s, %(genre)s, %(source)s, 
                %(link)s, %(image_url)s, %(published_at)s
            )
            ON CONFLICT (url_hash) DO NOTHING;
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_batch(cur, upsert_query, cards, page_size=100)
                conn.commit()
                logger.info(
                    "Database transaction committed: Batch upsert of %d cards completed.",
                    len(cards),
                )
                return len(cards)
        except Exception as e:
            logger.error("Failed to batch upsert articles into database: %s", e)
            return 0

    def get_recent_articles(self, limit: int = 150) -> List[Dict[str, Any]]:
        """Queries recent articles ordered by published_at DESC for deck feed verification."""
        if self.is_mock:
            sorted_cards = sorted(
                self._mock_records,
                key=lambda x: x.get("published_at", ""),
                reverse=True,
            )
            return sorted_cards[:limit]

        query = """
            SELECT id, url_hash, headline, summary, genre, source, link, image_url, published_at, created_at
            FROM articles
            ORDER BY published_at DESC
            LIMIT %s;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (limit,))
                    rows = cur.fetchall()
                    return [dict(r) for r in rows]
        except Exception as e:
            logger.error("Failed to query recent articles: %s", e)
            return []
