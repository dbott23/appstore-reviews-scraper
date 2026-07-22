"""Apple App Store scraper using the public iTunes RSS and Search APIs."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

SEARCH_URL = "https://itunes.apple.com/search"
LOOKUP_URL = "https://itunes.apple.com/lookup"


async def search_apps(
    client: httpx.AsyncClient, term: str, country: str = "us", limit: int = 5
) -> list[dict[str, Any]]:
    resp = await client.get(
        SEARCH_URL,
        params={"term": term, "entity": "software", "country": country, "limit": limit},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


async def lookup_app(
    client: httpx.AsyncClient, app_id: str, country: str = "us"
) -> dict[str, Any] | None:
    resp = await client.get(
        LOOKUP_URL, params={"id": app_id, "country": country}, timeout=30
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


async def get_reviews(
    client: httpx.AsyncClient,
    app_id: str,
    app_name: str,
    country: str = "us",
    max_reviews: int = 100,
    sort: str = "mostrecent",
) -> list[dict[str, Any]]:
    """Fetch reviews via the iTunes RSS JSON feed. Up to 500 reviews (10 pages × 50)."""
    reviews: list[dict[str, Any]] = []
    for page in range(1, 11):
        if len(reviews) >= max_reviews:
            break
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby={sort}/json"
        try:
            resp = await client.get(url, timeout=30)
            if resp.status_code == 404:
                break
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            break

        entries = (data.get("feed") or {}).get("entry") or []
        if not entries:
            break

        # First entry on page 1 is app metadata, not a review
        if page == 1 and isinstance(entries, list):
            entries = entries[1:]

        for entry in entries:
            if len(reviews) >= max_reviews:
                break
            reviews.append(_parse_review(entry, app_id, app_name, country))

        await asyncio.sleep(0.5)

    return reviews


def _label(entry: dict, key: str) -> str | None:
    v = entry.get(key)
    if isinstance(v, dict):
        return v.get("label")
    return v


def _parse_review(
    entry: dict[str, Any], app_id: str, app_name: str, country: str
) -> dict[str, Any]:
    rating_raw = _label(entry, "im:rating")
    try:
        rating = int(rating_raw) if rating_raw else None
    except (ValueError, TypeError):
        rating = None

    author_node = entry.get("author") or {}
    author_name = (author_node.get("name") or {}).get("label")

    return {
        "store": "apple",
        "appId": app_id,
        "appName": app_name,
        "country": country,
        "reviewId": _label(entry, "id"),
        "title": _label(entry, "title"),
        "text": _label(entry, "content"),
        "rating": rating,
        "author": author_name,
        "version": _label(entry, "im:version"),
        "date": _label(entry, "updated"),
        "thumbsUp": None,
        "replyText": None,
        "url": f"https://apps.apple.com/{country}/app/id{app_id}",
    }
