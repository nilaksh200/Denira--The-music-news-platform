"""
Denira Desktop — Feed Configuration & Endpoint Directory
Defines verified RSS/Atom feeds, Reddit community sources, and genre-matched fallback artwork.
"""

from typing import TypedDict, List, Dict


class FeedConfig(TypedDict):
    name: str
    url: str
    genre: str


class SubredditConfig(TypedDict):
    name: str
    subreddit: str
    url: str
    genre: str


# ------------------------------------------------------------------------------
# Verified RSS Feeds Directory (40+ publications across all core music genres)
# ------------------------------------------------------------------------------
FEEDS_CONFIG: List[FeedConfig] = [
    # --- Rock / Indie ---
    {
        "name": "Pitchfork",
        "url": "https://pitchfork.com/feed/feed-news/rss",
        "genre": "Rock & Indie",
    },
    {
        "name": "Stereogum",
        "url": "https://www.stereogum.com/feed/",
        "genre": "Rock & Indie",
    },
    {
        "name": "Consequence",
        "url": "https://consequence.net/feed/",
        "genre": "Rock & Indie",
    },
    {
        "name": "NME",
        "url": "https://www.nme.com/feed",
        "genre": "Rock & Indie",
    },
    {
        "name": "Spin",
        "url": "https://www.spin.com/feed/",
        "genre": "Rock & Indie",
    },
    {
        "name": "The Line of Best Fit",
        "url": "https://www.thelineofbestfit.com/feed",
        "genre": "Rock & Indie",
    },
    {
        "name": "DIY Mag",
        "url": "https://diymag.com/feed",
        "genre": "Rock & Indie",
    },
    {
        "name": "Louder Sound",
        "url": "https://www.loudersound.com/feeds/all",
        "genre": "Rock & Indie",
    },
    {
        "name": "BrooklynVegan",
        "url": "https://www.brooklynvegan.com/feed/",
        "genre": "Rock & Indie",
    },

    # --- Hip-Hop / R&B ---
    {
        "name": "XXL Mag",
        "url": "https://www.xxlmag.com/feed/",
        "genre": "Hip-Hop",
    },
    {
        "name": "HipHopDX",
        "url": "https://hiphopdx.com/feed",
        "genre": "Hip-Hop",
    },
    {
        "name": "HotNewHipHop",
        "url": "https://www.hotnewhiphop.com/rss/",
        "genre": "Hip-Hop",
    },
    {
        "name": "Complex Music",
        "url": "https://www.complex.com/music/rss",
        "genre": "Hip-Hop",
    },
    {
        "name": "AllHipHop",
        "url": "https://allhiphop.com/feed/",
        "genre": "Hip-Hop",
    },
    {
        "name": "The Source",
        "url": "https://thesource.com/feed/",
        "genre": "Hip-Hop",
    },
    {
        "name": "Rap-Up",
        "url": "https://www.rap-up.com/feed/",
        "genre": "Hip-Hop",
    },

    # --- Electronic / Club ---
    {
        "name": "Resident Advisor",
        "url": "https://ra.co/feed.xml",
        "genre": "Electronic",
    },
    {
        "name": "Mixmag",
        "url": "https://mixmag.net/rss.xml",
        "genre": "Electronic",
    },
    {
        "name": "Attack Magazine",
        "url": "https://www.attackmagazine.com/feed/",
        "genre": "Electronic",
    },
    {
        "name": "Dancing Astronaut",
        "url": "https://dancingastronaut.com/feed/",
        "genre": "Electronic",
    },
    {
        "name": "EDM Sauce",
        "url": "https://www.edmsauce.com/feed/",
        "genre": "Electronic",
    },
    {
        "name": "We Rave You",
        "url": "https://weraveyou.com/feed/",
        "genre": "Electronic",
    },
    {
        "name": "DJ Times",
        "url": "https://djtimes.com/feed/",
        "genre": "Electronic",
    },
    {
        "name": "EDM.com",
        "url": "https://edm.com/.rss/full/",
        "genre": "Electronic",
    },
    {
        "name": "DJ Mag",
        "url": "https://djmag.com/rss.xml",
        "genre": "Electronic",
    },

    # --- Metal / Hardcore ---
    {
        "name": "Metal Injection",
        "url": "https://metalinjection.net/feed",
        "genre": "Metal",
    },
    {
        "name": "MetalSucks",
        "url": "https://www.metalsucks.net/feed/",
        "genre": "Metal",
    },
    {
        "name": "Blabbermouth",
        "url": "https://blabbermouth.net/feed",
        "genre": "Metal",
    },
    {
        "name": "Decibel Magazine",
        "url": "https://www.decibelmagazine.com/feed/",
        "genre": "Metal",
    },
    {
        "name": "BraveWords",
        "url": "https://bravewords.com/rss/news.xml",
        "genre": "Metal",
    },
    {
        "name": "Heavy Consequence",
        "url": "https://consequence.net/category/heavy-consequence/feed/",
        "genre": "Metal",
    },
    {
        "name": "Kerrang!",
        "url": "https://www.kerrang.com/feed",
        "genre": "Metal",
    },

    # --- Pop / Mainstream / Industry ---
    {
        "name": "Billboard",
        "url": "https://www.billboard.com/c/music/music-news/feed/",
        "genre": "Pop",
    },
    {
        "name": "Rolling Stone",
        "url": "https://www.rollingstone.com/music/music-news/feed/",
        "genre": "Pop",
    },
    {
        "name": "Music Business Worldwide",
        "url": "https://www.musicbusinessworldwide.com/feed/",
        "genre": "Pop",
    },
    {
        "name": "Complete Music Update",
        "url": "https://completemusicupdate.com/feed/",
        "genre": "Pop",
    },
    {
        "name": "Idolator",
        "url": "https://www.idolator.com/feed",
        "genre": "Pop",
    },

    # --- Audio Gear & Production ---
    {
        "name": "Gearnews",
        "url": "https://www.gearnews.com/feed/",
        "genre": "Audio & Gear",
    },
    {
        "name": "Synthtopia",
        "url": "https://www.synthtopia.com/feed/",
        "genre": "Audio & Gear",
    },
    {
        "name": "MusicRadar",
        "url": "https://www.musicradar.com/feeds/all",
        "genre": "Audio & Gear",
    },
    {
        "name": "Guitar World",
        "url": "https://www.guitarworld.com/feeds/all",
        "genre": "Audio & Gear",
    },
    {
        "name": "Sound on Sound",
        "url": "https://www.soundonsound.com/rss",
        "genre": "Audio & Gear",
    },

    # --- Discovery / Underground ---
    {
        "name": "Bandcamp Daily",
        "url": "https://daily.bandcamp.com/feed",
        "genre": "Discovery",
    },
    {
        "name": "Stereofox",
        "url": "https://www.stereofox.com/feed/",
        "genre": "Discovery",
    },
]

# ------------------------------------------------------------------------------
# Curated Subreddit Endpoints (public new.json?limit=40)
# ------------------------------------------------------------------------------
REDDIT_USER_AGENT = "DeniraDesktop/1.0 (DesktopInshortsEngine; contact@deniramusic.org)"

SUBREDDITS_CONFIG: List[SubredditConfig] = [
    {
        "name": "r/indieheads",
        "subreddit": "indieheads",
        "url": "https://www.reddit.com/r/indieheads/new.json?limit=40",
        "genre": "Rock & Indie",
    },
    {
        "name": "r/hiphopheads",
        "subreddit": "hiphopheads",
        "url": "https://www.reddit.com/r/hiphopheads/new.json?limit=40",
        "genre": "Hip-Hop",
    },
    {
        "name": "r/popheads",
        "subreddit": "popheads",
        "url": "https://www.reddit.com/r/popheads/new.json?limit=40",
        "genre": "Pop",
    },
    {
        "name": "r/electronicmusic",
        "subreddit": "electronicmusic",
        "url": "https://www.reddit.com/r/electronicmusic/new.json?limit=40",
        "genre": "Electronic",
    },
    {
        "name": "r/metal",
        "subreddit": "metal",
        "url": "https://www.reddit.com/r/metal/new.json?limit=40",
        "genre": "Metal",
    },
]

# ------------------------------------------------------------------------------
# Genre-Matched Dark Aesthetic Fallback Artwork
# High-resolution, dark atmospheric imagery curated for desktop 50/50 split deck
# ------------------------------------------------------------------------------
GENRE_FALLBACK_IMAGES: Dict[str, str] = {
    "Rock & Indie": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80",
    "Hip-Hop": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1200&q=80",
    "Electronic": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1200&q=80",
    "Metal": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=1200&q=80",
    "Pop": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=1200&q=80",
    "Audio & Gear": "https://images.unsplash.com/photo-1598653222000-6b7b7a552625?auto=format&fit=crop&w=1200&q=80",
    "Discovery": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
}

DEFAULT_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80"


def get_fallback_image(genre: str) -> str:
    """Return a genre-matched dark aesthetic wallpaper URL."""
    return GENRE_FALLBACK_IMAGES.get(genre, DEFAULT_FALLBACK_IMAGE)
