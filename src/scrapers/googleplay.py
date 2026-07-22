"""Google Play Store scraper using the google-play-scraper library."""

from __future__ import annotations

import asyncio
import functools
from typing import Any


def _run_sync(fn, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, functools.partial(fn, *args, **kwargs))


async def lookup_app(app_id: str, country: str = "us") -> dict[str, Any] | None:
    from google_play_scraper import app
    try:
        return await _run_sync(app, app_id, lang="en", country=country)
    except Exception:
        return None


async def get_reviews(
    app_id: str,
    app_name: str,
    country: str = "us",
    max_reviews: int = 100,
    sort: str = "newest",
) -> list[dict[str, Any]]:
    from google_play_scraper import reviews, Sort

    sort_map = {"newest": Sort.NEWEST, "helpful": Sort.MOST_RELEVANT}
    gp_sort = sort_map.get(sort, Sort.NEWEST)

    result, _ = await _run_sync(
        reviews, app_id, lang="en", country=country, sort=gp_sort, count=max_reviews
    )
    return [_parse_review(r, app_id, app_name, country) for r in (result or [])]


def _parse_review(r: dict[str, Any], app_id: str, app_name: str, country: str) -> dict[str, Any]:
    at = r.get("at")
    date_str = at.isoformat() if at else None
    return {
        "store": "google",
        "appId": app_id,
        "appName": app_name,
        "country": country,
        "reviewId": r.get("reviewId"),
        "title": None,
        "text": r.get("content"),
        "rating": r.get("score"),
        "author": r.get("userName"),
        "version": r.get("reviewCreatedVersion") or r.get("appVersion"),
        "date": date_str,
        "thumbsUp": r.get("thumbsUpCount"),
        "replyText": r.get("replyContent"),
        "url": f"https://play.google.com/store/apps/details?id={app_id}",
    }
