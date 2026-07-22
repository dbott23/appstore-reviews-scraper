"""App Store Reviews Scraper — scrape reviews from Apple App Store and Google Play."""

import asyncio

import httpx
from apify import Actor

from src.scrapers import appstore, googleplay


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}

        apple_ids: list[str] = [str(x) for x in (inp.get("appleAppIds") or [])]
        google_ids: list[str] = inp.get("googlePlayIds") or []
        search_terms: list[str] = inp.get("searchTerms") or []
        country: str = (inp.get("country") or "us").lower().strip()
        max_reviews: int = max(1, min(int(inp.get("maxReviewsPerApp") or 100), 500))
        sort: str = inp.get("sortBy") or "newest"
        apple_sort = "mostrecent" if sort == "newest" else "mosthelpful"

        if not any([apple_ids, google_ids, search_terms]):
            await Actor.fail(
                status_message="Provide at least one of: appleAppIds, googlePlayIds, or searchTerms."
            )
            return

        total = 0

        async with httpx.AsyncClient() as client:

            # Search terms → resolve Apple App Store app IDs
            if search_terms:
                for term in search_terms:
                    Actor.log.info(f"Searching Apple App Store for: {term!r}")
                    try:
                        found = await appstore.search_apps(client, term, country=country, limit=3)
                        for app_info in found:
                            aid = str(app_info.get("trackId", ""))
                            if aid and aid not in apple_ids:
                                apple_ids.append(aid)
                                Actor.log.info(f"  Found: {app_info.get('trackName')} (id={aid})")
                    except Exception as exc:
                        Actor.log.warning(f"Apple search failed for {term!r}: {exc}")

            # Apple App Store reviews
            for app_id in apple_ids:
                Actor.log.info(f"Fetching Apple App Store reviews — app id: {app_id}")
                try:
                    app_info = await appstore.lookup_app(client, app_id, country=country)
                    app_name = (app_info or {}).get("trackName") or app_id
                    reviews = await appstore.get_reviews(
                        client, app_id, app_name,
                        country=country, max_reviews=max_reviews, sort=apple_sort,
                    )
                except Exception as exc:
                    Actor.log.warning(f"Apple reviews failed for {app_id}: {exc}")
                    continue
                if reviews:
                    await Actor.push_data(reviews)
                    total += len(reviews)
                Actor.log.info(f"  → {len(reviews)} reviews (total: {total})")

            # Google Play reviews
            for app_id in google_ids:
                Actor.log.info(f"Fetching Google Play reviews — package: {app_id}")
                try:
                    app_info = await googleplay.lookup_app(app_id, country=country)
                    app_name = (app_info or {}).get("title") or app_id
                    reviews = await googleplay.get_reviews(
                        app_id, app_name,
                        country=country, max_reviews=max_reviews, sort=sort,
                    )
                except Exception as exc:
                    Actor.log.warning(f"Google Play reviews failed for {app_id}: {exc}")
                    continue
                if reviews:
                    await Actor.push_data(reviews)
                    total += len(reviews)
                Actor.log.info(f"  → {len(reviews)} reviews (total: {total})")

        Actor.log.info(f"Done. Total reviews pushed: {total}")


if __name__ == "__main__":
    asyncio.run(main())
