"""
Denira Desktop — Autonomous 6-Hour Ingestion & Editorial Pipeline
Orchestrates multi-source ingestion, hash deduplication, GroqCloud synthesis, and Supabase persistence.
Operates strictly within permanent zero-cost ($0 / ₹0) cloud constraints.
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

# Ensure project root is on sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from backend.db.client import DatabaseClient
from backend.ingestion.scraper import AsyncNewsIngester, HarvestedArticle
from backend.summarizer.groq_client import AsyncSummarizer, SynthesizedCard

# Load environment configuration
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("denira.pipeline")


def balance_candidates_by_genre(
    candidates: List[HarvestedArticle], target_limit: int
) -> List[HarvestedArticle]:
    """
    Sorts candidates by recency and distributes selections across genres to ensure
    diverse editorial deck representation (Rock & Indie, Electronic, Hip-Hop, Pop, Metal, Gear, Discovery).
    """
    if len(candidates) <= target_limit:
        return candidates

    # Group by genre
    by_genre = defaultdict(list)
    for c in candidates:
        by_genre[c["genre"]].append(c)

    # Sort each genre group by published_at DESC
    for genre in by_genre:
        by_genre[genre].sort(
            key=lambda x: x.get("published_at", ""),
            reverse=True,
        )

    # Round-robin allocation across genres until target_limit is reached
    selected: List[HarvestedArticle] = []
    genre_names = list(by_genre.keys())

    # Calculate fair share per genre
    fair_share = max(1, target_limit // len(genre_names)) if genre_names else target_limit
    remaining_slots = target_limit

    # First pass: Allocate fair share from each genre
    for genre in genre_names:
        if remaining_slots <= 0:
            break
        take = min(fair_share, remaining_slots)
        slice_items = by_genre[genre][:take]
        selected.extend(slice_items)
        by_genre[genre] = by_genre[genre][len(slice_items):]
        remaining_slots -= len(slice_items)

    # Second pass: Fill remaining slots by pure recency from remaining candidates
    if remaining_slots > 0:
        leftover: List[HarvestedArticle] = []
        for genre in genre_names:
            leftover.extend(by_genre[genre])
        leftover.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        selected.extend(leftover[:remaining_slots])

    return selected[:target_limit]


async def run_pipeline(
    limit: int = 10,
    dry_run: bool = False,
    lookback_hours: int = 48,
) -> Dict[str, Any]:
    """
    Executes the full end-to-end autonomous ingestion, filtering, summarization,
    and database persistence workflow.
    """
    cycle_start = time.time()
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("\n" + "=" * 80)
    print(" DENIRA DESKTOP — HOURLY AUTONOMOUS INGESTION & EDITORIAL PIPELINE")
    print(f" Cycle Execution Started: {timestamp_str}")
    print(f" Configuration: Limit={limit} | DryRun={dry_run} | Lookback={lookback_hours}h")
    print("=" * 80 + "\n")

    # --------------------------------------------------------------------------
    # Step 1: Ingest Candidate Articles Across All Sources
    # --------------------------------------------------------------------------
    logger.info("[Step 1/5] Initiating multi-source async ingestion...")
    ingester = AsyncNewsIngester(concurrency_limit=15, timeout_seconds=10.0)
    harvested = await ingester.harvest_all()
    harvested_count = len(harvested)
    logger.info("Harvest complete: %d candidate articles gathered.", harvested_count)

    # --------------------------------------------------------------------------
    # Step 2: Query Existing URL Hashes to Pre-Filter
    # --------------------------------------------------------------------------
    logger.info("[Step 2/5] Connecting to database for deduplication hashes...")
    db_client = DatabaseClient()
    existing_hashes: Set[str] = db_client.get_existing_hashes(hours_lookback=lookback_hours)

    # --------------------------------------------------------------------------
    # Step 3: Filter Unseen Stories & Balance by Genre
    # --------------------------------------------------------------------------
    logger.info("[Step 3/5] Deduplicating candidate stream...")
    unseen_candidates = [
        item for item in harvested if item["url_hash"] not in existing_hashes
    ]
    unseen_count = len(unseen_candidates)
    seen_filtered_count = harvested_count - unseen_count

    logger.info(
        "Deduplication complete: %d unseen candidates remaining (%d seen items skipped).",
        unseen_count,
        seen_filtered_count,
    )

    # Cap to requested limit with genre balancing
    prioritized_candidates = balance_candidates_by_genre(unseen_candidates, limit)
    prioritized_count = len(prioritized_candidates)

    logger.info(
        "Editorial batch capped to top %d freshest stories across diverse genres.",
        prioritized_count,
    )

    # --------------------------------------------------------------------------
    # Step 4: AI Summarization via GroqCloud
    # --------------------------------------------------------------------------
    summarized_cards: List[SynthesizedCard] = []
    if prioritized_candidates:
        logger.info(
            "[Step 4/5] Initiating GroqCloud batch summarization (%s)...",
            "DRY-RUN" if dry_run else "LIVE INFERENCE",
        )
        summarizer = AsyncSummarizer()
        summarized_cards = await summarizer.summarize_batch(
            prioritized_candidates,
            max_concurrency=5,
            inter_task_delay=0.5,
        )
    else:
        logger.info("[Step 4/5] No fresh candidates to summarize in this cycle.")

    summarized_count = len(summarized_cards)

    # --------------------------------------------------------------------------
    # Step 5: Database Persistence
    # --------------------------------------------------------------------------
    committed_count = 0
    if dry_run:
        logger.info("[Step 5/5] DRY-RUN enabled: Skipping database commit.")
        committed_count = summarized_count
    elif summarized_cards:
        logger.info("[Step 5/5] Persisting %d cards to Supabase PostgreSQL...", summarized_count)
        committed_count = db_client.upsert_articles(summarized_cards)
    else:
        logger.info("[Step 5/5] Zero cards to commit.")

    cycle_duration = time.time() - cycle_start

    # --------------------------------------------------------------------------
    # Print Comprehensive Cycle Report
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print(" HOURLY PIPELINE CYCLE EXECUTION REPORT")
    print("-" * 80)
    print(f" Cycle Duration                  : {cycle_duration:.2f} seconds")
    print(f" Total Candidates Harvested      : {harvested_count}")
    print(f" Previously Seen (Skipped)       : {seen_filtered_count}")
    print(f" Fresh Candidates Available      : {unseen_count}")
    print(f" Capped Editorial Batch Target   : {prioritized_count}")
    print(f" Successfully Summarized Cards   : {summarized_count}")
    print(f" Persisted Cards to Database     : {committed_count} {'(DRY-RUN)' if dry_run else ''}")
    print("-" * 80)

    # Genre breakdown of generated cards
    genre_breakdown = defaultdict(int)
    for c in summarized_cards:
        genre_breakdown[c["genre"]] += 1

    print(" EDITORIAL DECK GENRE ALLOCATION:")
    for g, count in sorted(genre_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {g:<25} : {count:>4} cards")

    print("\n" + "=" * 80)
    print(" PIPELINE EXECUTION FINISHED SUCCESSFULLY")
    print("=" * 80 + "\n")

    return {
        "harvested": harvested_count,
        "seen_skipped": seen_filtered_count,
        "prioritized": prioritized_count,
        "summarized": summarized_count,
        "committed": committed_count,
        "duration_seconds": cycle_duration,
        "dry_run": dry_run,
    }


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments for the pipeline runner."""
    parser = argparse.ArgumentParser(
        description="Denira Desktop Hourly Autonomous Ingestion & Editorial Pipeline"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum candidate stories to process per cycle (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate cycle execution without committing records to PostgreSQL",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=48,
        help="Hours lookback window for deduplication hash checks (default: 48)",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    try:
        asyncio.run(
            run_pipeline(
                limit=args.limit,
                dry_run=args.dry_run,
                lookback_hours=args.lookback,
            )
        )
    except KeyboardInterrupt:
        logger.info("Pipeline execution cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Fatal pipeline execution error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
