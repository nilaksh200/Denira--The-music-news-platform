"""Denira Desktop Ingestion Package."""

from backend.ingestion.feeds import FEEDS_CONFIG, SUBREDDITS_CONFIG, get_fallback_image
from backend.ingestion.scraper import AsyncNewsIngester, HarvestedArticle

__all__ = [
    "FEEDS_CONFIG",
    "SUBREDDITS_CONFIG",
    "get_fallback_image",
    "AsyncNewsIngester",
    "HarvestedArticle",
]
