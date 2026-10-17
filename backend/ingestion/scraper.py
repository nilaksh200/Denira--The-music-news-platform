"""
Denira Desktop — Multi-Source Asynchronous Ingestion Engine
Ingests candidates across 40+ RSS/Atom feeds and curated Reddit communities.
Extracts clean headlines, summaries, canonical URLs, SHA-256 hashes, and cover imagery.
"""

import asyncio
import hashlib
import html
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional, Tuple, TypedDict

import feedparser
import httpx

from backend.ingestion.feeds import (
    DEFAULT_FALLBACK_IMAGE,
    FEEDS_CONFIG,
    FeedConfig,
    REDDIT_USER_AGENT,
    SUBREDDITS_CONFIG,
    SubredditConfig,
    get_fallback_image,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("denira.ingestion")

# Regex helpers for HTML cleanup and image extraction
IMG_SRC_PATTERN = re.compile(
    r'<img[^>]+(?:src|data-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp|avif)[^"\']*)["\']',
    re.IGNORECASE,
)
GENERIC_IMG_PATTERN = re.compile(
    r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


class HarvestedArticle(TypedDict):
    title: str
    link: str
    raw_summary: str
    source: str
    genre: str
    image_url: str
    url_hash: str
    published_at: str
    has_custom_image: bool


def clean_text(raw_html: Optional[str]) -> str:
    """Strips HTML tags, resolves HTML entities, and normalizes whitespace."""
    if not raw_html:
        return ""
    # Strip HTML tags
    text = HTML_TAG_PATTERN.sub(" ", raw_html)
    # Decode entities like &amp;, &quot;, &#8217;
    text = html.unescape(text)
    # Clean common feed artifacts (e.g. "The post ... appeared first on ...")
    text = re.sub(r"The post .* appeared first on .*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Read more \.\.\.", "", text, flags=re.IGNORECASE)
    # Normalize consecutive whitespace
    return " ".join(text.split()).strip()


def compute_url_hash(url: str) -> str:
    """Computes a SHA-256 hash of the canonical URL."""
    canonical = url.strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_published_date(entry: Any) -> str:
    """Extracts published date as ISO-8601 string or defaults to UTC now."""
    # Check feedparser standard date fields
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed_struct = getattr(entry, field, None) or entry.get(field)
        if parsed_struct:
            try:
                dt = datetime(*parsed_struct[:6], tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass

    for field in ("published", "updated", "pubDate"):
        date_str = getattr(entry, field, None) or entry.get(field)
        if date_str:
            try:
                dt = parsedate_to_datetime(date_str)
                return dt.isoformat()
            except Exception:
                pass

    return datetime.now(timezone.utc).isoformat()


def extract_rss_image(entry: Any, summary_html: str) -> Tuple[Optional[str], bool]:
    """
    Multi-strategy cover image extraction:
    1. media_content / media_thumbnail
    2. enclosures with image MIME type
    3. <img> src in HTML summary / content
    """
    # Strategy 1: media_content
    media_content = entry.get("media_content", [])
    if isinstance(media_content, list):
        for item in media_content:
            if isinstance(item, dict) and "url" in item:
                url = item["url"]
                mime = item.get("type", "")
                if mime.startswith("image/") or any(
                    url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")
                ):
                    return url, True

    # Strategy 2: media_thumbnail
    media_thumb = entry.get("media_thumbnail", [])
    if isinstance(media_thumb, list):
        for item in media_thumb:
            if isinstance(item, dict) and "url" in item:
                return item["url"], True

    # Strategy 3: enclosures
    enclosures = entry.get("enclosures", [])
    if isinstance(enclosures, list):
        for enc in enclosures:
            if isinstance(enc, dict):
                url = enc.get("href") or enc.get("url")
                enc_type = enc.get("type", "")
                if url and (
                    enc_type.startswith("image/")
                    or any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp"))
                ):
                    return url, True

    # Strategy 4: <img> tag in HTML summary or content:encoded
    raw_blobs = [summary_html]
    content_list = entry.get("content", [])
    if isinstance(content_list, list):
        for c in content_list:
            if isinstance(c, dict) and "value" in c:
                raw_blobs.append(c["value"])

    for blob in raw_blobs:
        if blob:
            match = IMG_SRC_PATTERN.search(blob) or GENERIC_IMG_PATTERN.search(blob)
            if match:
                img_candidate = match.group(1).strip()
                # Exclude tracking pixels or 1x1 gifs
                if (
                    img_candidate.startswith("http")
                    and "tracking" not in img_candidate.lower()
                    and "pixel" not in img_candidate.lower()
                    and "spacer" not in img_candidate.lower()
                ):
                    return img_candidate, True

    return None, False


class AsyncNewsIngester:
    """High-throughput asynchronous news ingester across RSS and Reddit."""

    def __init__(
        self,
        concurrency_limit: int = 15,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.timeout = httpx.Timeout(
            connect=5.0,
            read=timeout_seconds,
            write=5.0,
            pool=5.0,
        )
        self.limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=50,
        )
        self.default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 "
                "DeniraDesktop/1.0"
            ),
            "Accept": (
                "application/rss+xml, application/xml, text/xml, "
                "application/atom+xml, application/json, text/html;q=0.9, */*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch_rss_feed(
        self,
        client: httpx.AsyncClient,
        feed: FeedConfig,
    ) -> List[HarvestedArticle]:
        """Fetches and parses a single RSS/Atom feed asynchronously."""
        async with self.semaphore:
            try:
                response = await client.get(
                    feed["url"],
                    headers=self.default_headers,
                    follow_redirects=True,
                )
                if response.status_code != 200:
                    logger.warning(
                        "RSS feed '%s' returned status %d",
                        feed["name"],
                        response.status_code,
                    )
                    return []

                # Parse feed content in a thread pool to avoid blocking the event loop
                parsed = await asyncio.to_thread(feedparser.parse, response.content)
                articles: List[HarvestedArticle] = []

                for entry in parsed.entries:
                    title = clean_text(entry.get("title", ""))
                    link = entry.get("link", "").strip()

                    # Require valid headline and link
                    if not title or not link or not link.startswith("http"):
                        continue

                    raw_summary_html = (
                        entry.get("summary", "")
                        or entry.get("description", "")
                        or ""
                    )
                    clean_summary = clean_text(raw_summary_html)

                    # Extract image with multi-strategy waterfall
                    img_url, has_custom = extract_rss_image(entry, raw_summary_html)
                    if not img_url:
                        img_url = get_fallback_image(feed["genre"])
                        has_custom = False

                    articles.append(
                        {
                            "title": title,
                            "link": link,
                            "raw_summary": clean_summary,
                            "source": feed["name"],
                            "genre": feed["genre"],
                            "image_url": img_url,
                            "url_hash": compute_url_hash(link),
                            "published_at": parse_published_date(entry),
                            "has_custom_image": has_custom,
                        }
                    )

                logger.info(
                    "Harvested %d articles from '%s'",
                    len(articles),
                    feed["name"],
                )
                return articles

            except Exception as e:
                logger.warning(
                    "Failed to fetch RSS feed '%s' (%s): %s",
                    feed["name"],
                    feed["url"],
                    type(e).__name__,
                )
                return []

    async def _staggered_fetch_subreddit(
        self,
        client: httpx.AsyncClient,
        sub: SubredditConfig,
        delay_index: int,
    ) -> List[HarvestedArticle]:
        """Staggers requests to Reddit by 400ms per endpoint to avoid burst 429 rate limits."""
        if delay_index > 0:
            await asyncio.sleep(0.4 * delay_index)
        return await self.fetch_subreddit(client, sub)

    async def fetch_subreddit(
        self,
        client: httpx.AsyncClient,
        sub: SubredditConfig,
    ) -> List[HarvestedArticle]:
        """
        Fetches curated subreddits via public new.json?limit=40 endpoint.
        Falls back to public RSS stream if JSON is blocked by anti-scraping filters.
        """
        async with self.semaphore:
            reddit_headers = {
                "User-Agent": REDDIT_USER_AGENT,
                "Accept": "application/json, text/plain, */*",
            }

            try:
                response = await client.get(
                    sub["url"],
                    headers=reddit_headers,
                    follow_redirects=True,
                )

                # If JSON endpoint is allowed, parse JSON posts
                if response.status_code == 200:
                    try:
                        data = response.json()
                        children = data.get("data", {}).get("children", [])
                        return self._parse_reddit_json(children, sub)
                    except Exception:
                        pass  # Fall through to RSS fallback

                # If JSON was rate-limited or blocked (e.g. 403), use public RSS
                rss_fallback_url = (
                    f"https://www.reddit.com/r/{sub['subreddit']}/new/.rss?limit=40"
                )
                rss_headers = {
                    "User-Agent": self.default_headers["User-Agent"],
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                }
                fallback_resp = await client.get(
                    rss_fallback_url,
                    headers=rss_headers,
                    follow_redirects=True,
                )

                if fallback_resp.status_code == 200:
                    parsed = await asyncio.to_thread(
                        feedparser.parse, fallback_resp.content
                    )
                    return self._parse_reddit_feed(parsed.entries, sub)

                logger.warning(
                    "Subreddit '%s' unavailable (JSON: %d, RSS: %d)",
                    sub["name"],
                    response.status_code,
                    fallback_resp.status_code,
                )
                return []

            except Exception as e:
                logger.warning(
                    "Failed to fetch subreddit '%s': %s",
                    sub["name"],
                    type(e).__name__,
                )
                return []

    def _parse_reddit_json(
        self,
        children: List[Dict[str, Any]],
        sub: SubredditConfig,
    ) -> List[HarvestedArticle]:
        """Parses native Reddit JSON post structure."""
        articles: List[HarvestedArticle] = []

        for item in children:
            post = item.get("data", {})
            title = clean_text(post.get("title", ""))
            # Use outbound external link if available, otherwise Reddit permalink
            permalink = f"https://www.reddit.com{post.get('permalink', '')}"
            link = post.get("url") or permalink

            if not title or not link:
                continue

            # Extract image
            img_url: Optional[str] = None
            has_custom = False

            # Check preview image
            previews = post.get("preview", {}).get("images", [])
            if previews and isinstance(previews, list):
                source_img = previews[0].get("source", {}).get("url")
                if source_img:
                    img_url = html.unescape(source_img)
                    has_custom = True

            # Check thumbnail
            if not img_url:
                thumb = post.get("thumbnail")
                if thumb and thumb.startswith("http"):
                    img_url = thumb
                    has_custom = True

            if not img_url:
                img_url = get_fallback_image(sub["genre"])
                has_custom = False

            created_utc = post.get("created_utc")
            if created_utc:
                pub_date = datetime.fromtimestamp(
                    created_utc, tz=timezone.utc
                ).isoformat()
            else:
                pub_date = datetime.now(timezone.utc).isoformat()

            raw_summary = clean_text(post.get("selftext", "") or title)

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "raw_summary": raw_summary,
                    "source": sub["name"],
                    "genre": sub["genre"],
                    "image_url": img_url,
                    "url_hash": compute_url_hash(link),
                    "published_at": pub_date,
                    "has_custom_image": has_custom,
                }
            )

        logger.info(
            "Harvested %d posts from '%s' (JSON)",
            len(articles),
            sub["name"],
        )
        return articles

    def _parse_reddit_feed(
        self,
        entries: List[Any],
        sub: SubredditConfig,
    ) -> List[HarvestedArticle]:
        """Parses Reddit Atom/RSS entries."""
        articles: List[HarvestedArticle] = []

        for entry in entries:
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "").strip()

            if not title or not link:
                continue

            raw_summary_html = entry.get("content", [{}])[0].get(
                "value", ""
            ) or entry.get("summary", "")
            clean_summary = clean_text(raw_summary_html)

            img_url, has_custom = extract_rss_image(entry, raw_summary_html)
            if not img_url:
                img_url = get_fallback_image(sub["genre"])
                has_custom = False

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "raw_summary": clean_summary or title,
                    "source": sub["name"],
                    "genre": sub["genre"],
                    "image_url": img_url,
                    "url_hash": compute_url_hash(link),
                    "published_at": parse_published_date(entry),
                    "has_custom_image": has_custom,
                }
            )

        logger.info(
            "Harvested %d posts from '%s' (RSS stream)",
            len(articles),
            sub["name"],
        )
        return articles

    async def harvest_all(
        self,
        custom_feeds: Optional[List[FeedConfig]] = None,
        custom_subreddits: Optional[List[SubredditConfig]] = None,
    ) -> List[HarvestedArticle]:
        """
        Executes an asynchronous harvest across all configured RSS and Reddit endpoints.
        Deduplicates in-flight entries by url_hash.
        """
        feeds = custom_feeds if custom_feeds is not None else FEEDS_CONFIG
        subreddits = (
            custom_subreddits if custom_subreddits is not None else SUBREDDITS_CONFIG
        )

        logger.info(
            "Initiating ingestion cycle across %d RSS feeds and %d subreddits...",
            len(feeds),
            len(subreddits),
        )

        async with httpx.AsyncClient(
            timeout=self.timeout,
            limits=self.limits,
            http2=False,
        ) as client:
            tasks = [
                self.fetch_rss_feed(client, feed) for feed in feeds
            ] + [
                self._staggered_fetch_subreddit(client, sub, idx)
                for idx, sub in enumerate(subreddits)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles: List[HarvestedArticle] = []
        seen_hashes = set()

        for res in results:
            if isinstance(res, list):
                for item in res:
                    if item["url_hash"] not in seen_hashes:
                        seen_hashes.add(item["url_hash"])
                        all_articles.append(item)
            elif isinstance(res, Exception):
                logger.error("Unhandled harvest task exception: %s", res)

        logger.info(
            "Harvest complete. Gathered %d unique articles (out of %d raw hashes).",
            len(all_articles),
            len(seen_hashes),
        )
        return all_articles


# ------------------------------------------------------------------------------
# Standalone CLI Test Entrypoint
# ------------------------------------------------------------------------------
async def run_diagnostics() -> None:
    """Executes a live test cycle, calculates metrics, and displays analytics."""
    print("=" * 80)
    print(" DENIRA DESKTOP — MULTI-SOURCE INGESTION ENGINE DIAGNOSTICS")
    print("=" * 80)

    start_time = datetime.now()
    ingester = AsyncNewsIngester(concurrency_limit=15, timeout_seconds=10.0)
    articles = await ingester.harvest_all()
    duration = (datetime.now() - start_time).total_seconds()

    # Aggregate statistics
    total_count = len(articles)
    source_stats: Dict[str, int] = {}
    genre_stats: Dict[str, int] = {}
    custom_image_count = 0

    for a in articles:
        source_stats[a["source"]] = source_stats.get(a["source"], 0) + 1
        genre_stats[a["genre"]] = genre_stats.get(a["genre"], 0) + 1
        if a["has_custom_image"]:
            custom_image_count += 1

    custom_image_pct = (
        (custom_image_count / total_count * 100) if total_count > 0 else 0
    )

    print("\n" + "-" * 80)
    print(" HARVEST PERFORMANCE SUMMARY")
    print("-" * 80)
    print(f"Total Unique Articles Harvested : {total_count}")
    print(f"Cycle Duration                   : {duration:.2f} seconds")
    print(
        f"Custom Images Extracted          : {custom_image_count} / {total_count} ({custom_image_pct:.1f}%)"
    )
    print(
        f"Fallback Artworks Applied        : {total_count - custom_image_count} / {total_count} ({100 - custom_image_pct:.1f}%)"
    )

    print("\n" + "-" * 80)
    print(" BREAKDOWN BY MUSIC GENRE")
    print("-" * 80)
    for genre, count in sorted(genre_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {genre:<25} : {count:>4} articles")

    print("\n" + "-" * 80)
    print(" BREAKDOWN BY PUBLICATION SOURCE (TOP 20)")
    print("-" * 80)
    sorted_sources = sorted(source_stats.items(), key=lambda x: x[1], reverse=True)
    for src, count in sorted_sources[:20]:
        print(f"  • {src:<28} : {count:>4} articles")

    print("\n" + "-" * 80)
    print(" SAMPLE HARVESTED EDITORIAL CARDS (5 PREVIEWS)")
    print("-" * 80)
    for i, a in enumerate(articles[:5], start=1):
        print(f"\n[Card #{i}] {a['source']} | Genre: {a['genre']}")
        print(f"Headline : {a['title']}")
        print(f"Link     : {a['link']}")
        print(f"Hash     : {a['url_hash'][:16]}...")
        print(f"Image    : {a['image_url'][:75]}...")
        print(f"Summary  : {a['raw_summary'][:140]}...")

    print("\n" + "=" * 80)
    print(" DIAGNOSTICS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
