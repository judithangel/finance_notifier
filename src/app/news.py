from __future__ import annotations
import datetime as dt
from typing import List, Dict, Iterable
from urllib.parse import quote_plus
import feedparser


def build_query(name: str, ticker: str) -> str:
    """
    Build a Google News search query for a company.
    """
    # Return a query combining company name, ticker, and finance keywords
    return f'("{name}" OR {ticker}) (stock OR aktie OR börse)'


def filter_titles(items: List[Dict[str, str]], required_keywords: Iterable[str] = ()) -> List[Dict[str, str]]:
    """
    Filter news items so that only those containing required keywords
    in their title are kept.
    """
    # If no required keywords, return items unchanged
    if not required_keywords:
        return items
    # Otherwise, keep only items whose title contains any keyword (case-insensitive)
    filtered = [
        item for item in items
        if any(keyword.lower() in item["title"].lower() for keyword in required_keywords)
    ]
    return filtered


def _google_news_rss_url(query: str, lang: str = "de", country: str = "DE") -> str:
    """
    Build a Google News RSS URL for a given query.
    """
    # Encode the query with quote_plus, append "when:12h"
    query_enc = quote_plus(f"{query} when:12h")
    # Construct and return the final RSS URL
    return f"https://news.google.com/rss/search?q={query_enc}&hl={lang}&gl={country}&ceid={country}:{lang}"

def fetch_headlines(
    query: str,
    limit: int = 2,
    lookback_hours: int = 12,
    lang: str = "de",
    country: str = "DE",
) -> List[Dict[str, str]]:
    """
    Fetch latest headlines from Google News RSS for a given query.

    Args:
        query (str): Search query (usually built with `build_query`).
        limit (int): Maximum number of news items to return.
        lookback_hours (int): Only include news not older than this.
        lang (str): Language code (e.g. "de", "en").
        country (str): Country code (e.g. "DE", "US").

    Returns:
        List[Dict[str, str]]: News items in the format:
            {
              "title": "Some headline",
              "source": "Publisher",
              "link": "https://original-article.com",
              "published": "2025-08-30T10:45:00+00:00"
            }

    Notes:
        - Uses `feedparser` to parse Google News RSS feeds.
        - Adds some buffer (fetch up to 3x requested items)
          before filtering out old articles.
        - Published time is ISO-8601 with UTC timezone if available.
    """
    rss_url = _google_news_rss_url(query, lang=lang, country=country)
    feed = feedparser.parse(rss_url)
    # Filter entries by publication time (lookback_hours) and collect title/source/link
    out = []
    for entry in feed.entries:
        print("for-loop")
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=lookback_hours)
        if dt.datetime(*entry.published_parsed[:6], tzinfo=dt.timezone.utc) < cutoff:
            continue
        # Extract publisher/source if available
        source = ""
        if hasattr(entry, "source") and getattr(entry.source, "title", ""):
            source = entry.source.title
        elif hasattr(entry, "tags") and entry.tags:
            source = entry.tags[0].term
        out.append({
            "title": entry.title,
            "source": source,
            "link": entry.link,
        })
        if len(out) >= limit:
            break
    print(out)
    return out
