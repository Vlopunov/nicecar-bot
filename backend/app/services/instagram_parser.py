import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


async def fetch_instagram_posts(username: str, count: int = 12) -> List[Dict]:
    """Fetch recent Instagram posts for portfolio import.

    Uses instaloader library. Requires INSTAGRAM_SESSION_ID for private profiles.
    Returns list of dicts with image_url, caption, timestamp, permalink.
    """
    try:
        import instaloader

        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_comments=False,
            download_geotags=False,
            save_metadata=False,
        )

        profile = instaloader.Profile.from_username(loader.context, username)
        posts = []
        for i, post in enumerate(profile.get_posts()):
            if i >= count:
                break
            posts.append({
                "image_url": post.url,
                "caption": post.caption or "",
                "timestamp": post.date_utc.isoformat(),
                "permalink": f"https://www.instagram.com/p/{post.shortcode}/",
                "hashtags": list(post.caption_hashtags) if post.caption_hashtags else [],
            })
        return posts
    except Exception as e:
        logger.error(f"Instagram parsing error: {e}")
        return []


def guess_category_from_hashtags(hashtags: list[str]) -> str | None:
    """Try to determine service category from Instagram hashtags."""
    mapping = {
        "антигравийная": "Антигравийная оклейка кузова",
        "ppf": "Антигравийная оклейка кузова",
        "оклейка": "Антигравийная оклейка кузова",
        "винил": "Оклейка виниловой плёнкой",
        "тонировка": "Тонировка стёкол",
        "полировка": "Полировка",
        "керамика": "Защитные покрытия",
        "химчистка": "Химчистка салона",
        "мойка": "Деликатная мойка",
        "перетяжка": "Перетяжка и восстановление салона",
        "шумоизоляция": "Шумоизоляция",
        "антикор": "Антикоррозийная обработка",
        "аквапринт": "Аквапринт",
    }

    for tag in hashtags:
        tag_lower = tag.lower()
        for keyword, category in mapping.items():
            if keyword in tag_lower:
                return category
    return None
