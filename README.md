# App Store & Google Play Reviews Scraper

Scrape user reviews from the **Apple App Store** and **Google Play Store** — no API key or account required. Search by keyword or provide app IDs directly. Extracts ratings, review text, author, version, and date for up to 500 reviews per app per run.

## What it does

- **Apple App Store:** Search by keyword (e.g. "spotify", "notion") to find the top matching apps, then scrape their reviews. Or provide numeric App Store IDs directly.
- **Google Play Store:** Provide package names (e.g. `com.spotify.music`) to scrape reviews directly.
- Supports filtering by **country** and sorting by **newest** or **most helpful**.
- Returns structured data ready to export as JSON, CSV, or Excel.

## Use cases

- **Reputation monitoring** — track what users say about your app over time
- **Competitor intelligence** — see what users love or hate about rival apps
- **Sentiment analysis** — feed reviews into NLP pipelines or AI models
- **Product research** — discover feature requests and pain points from real users
- **App Store Optimization (ASO)** — identify keywords users naturally use in reviews

## Input

| Field | Type | Description |
|---|---|---|
| `searchTerms` | string[] | Keywords to search on the Apple App Store (e.g. `["spotify", "notion"]`). Returns the top 3 matching apps per term. |
| `appleAppIds` | string[] | Numeric Apple App Store IDs (e.g. `["324684580"]`). Find the ID in the App Store URL: `apps.apple.com/us/app/name/id324684580` |
| `googlePlayIds` | string[] | Google Play package names (e.g. `["com.spotify.music"]`). Find it in the Play Store URL: `play.google.com/store/apps/details?id=com.spotify.music` |
| `country` | string | Two-letter country code (default: `us`). Controls which store region to scrape. |
| `maxReviewsPerApp` | integer | Max reviews per app, 1–500 (default: `100`). |
| `sortBy` | string | `newest` (default) or `helpful`. |

At least one of `searchTerms`, `appleAppIds`, or `googlePlayIds` must be provided.

> **Note:** Google Play search by keyword is not supported due to library limitations. For Google Play, provide package names directly.

## Output

Each result is one review with these fields:

```json
{
  "store": "apple",
  "appId": "324684580",
  "appName": "Spotify: Music and Podcasts",
  "country": "us",
  "reviewId": "12345678901",
  "title": "Best music app",
  "text": "I use this every single day. The recommendations are spot on.",
  "rating": 5,
  "author": "username123",
  "version": "9.1.66",
  "date": "2026-07-21T20:00:00",
  "thumbsUp": null,
  "replyText": null,
  "url": "https://apps.apple.com/us/app/spotify-music-and-podcasts/id324684580"
}
```

Google Play reviews include `thumbsUp` (helpful votes) and `replyText` (developer reply). Apple App Store reviews include `title` but not `thumbsUp`.

## Limits

| Store | Max reviews per app |
|---|---|
| Apple App Store | 500 (10 pages × 50 reviews) |
| Google Play | 500 per run |

Apple App Store only exposes the most recent ~500 reviews publicly. If an app has millions of reviews, only the latest 500 are accessible without the Apple Search Ads API.

## Example: scrape Spotify reviews from both stores

```json
{
  "searchTerms": ["spotify"],
  "googlePlayIds": ["com.spotify.music"],
  "country": "us",
  "maxReviewsPerApp": 100,
  "sortBy": "newest"
}
```

This will:
1. Search the Apple App Store for "spotify" → find the top 3 matching apps → scrape up to 100 reviews each
2. Scrape up to 100 Google Play reviews for `com.spotify.music`

## Pricing

This actor uses **Pay per result** pricing:

- **$1.00 per 1,000 reviews** scraped
- Typical run of 100 reviews costs **~$0.10**
- Platform usage costs are included — no extra compute charges

## Frequently asked questions

**Can I scrape reviews in other languages / countries?**
Yes. Set `country` to any two-letter country code (e.g. `de` for Germany, `jp` for Japan). Reviews and app metadata will reflect that regional store.

**Why does Apple App Store search return multiple apps?**
The iTunes Search API returns the top 3 results for your keyword. If you want a specific app, use its numeric App Store ID instead.

**How do I find a Google Play package name?**
Go to the app's Play Store page and look at the URL: `play.google.com/store/apps/details?id=com.example.app` — the package name is the value after `id=`.

**How do I find an Apple App Store ID?**
Go to the app's App Store page and look at the URL: `apps.apple.com/us/app/name/id324684580` — the ID is the number after `id`.

**Does this require a proxy?**
No. Both stores are accessed without proxies or authentication.

---

## More from dbott23

| Actor | What it does |
|---|---|
| [Trustpilot Reviews Scraper](https://apify.com/dbott23/trustpilot-reviews-scraper) | Export Trustpilot reviews to CSV or JSON — no API key needed |
| [B2B Reviews Scraper](https://apify.com/dbott23/b2b-reviews-scraper) | Pull reviews from G2, Capterra, and Trustpilot in one run |
| [Bluesky Posts Scraper](https://apify.com/dbott23/bluesky-posts-scraper) | Search and export Bluesky posts by keyword or user profile |
| [AI Brand Visibility Tracker](https://apify.com/dbott23/ai-brand-visibility-tracker) | Track how AI assistants mention your brand vs. competitors |
| [AI Citation Auditor](https://apify.com/dbott23/ai-citation-auditor) | Check if your website is cited by ChatGPT, Perplexity, and Gemini |
