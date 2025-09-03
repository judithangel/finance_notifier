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
    query = f"{name} {ticker} finance"
    return query


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
    return f"https://news.google.com/rss/search?q={query_enc}&hl={lang}-{country}&gl={country}&ceid={country}:{lang}"

def fetch_headlines(
    query: str,
    limit: int = 2,
    lookback_hours: int = 12,
    lang: str = "de",
    country: str = "DE",
) -> List[Dict[str, str]]:
    """
    Fetch latest headlines from Google News RSS for a given query.
    """
    rss_url = _google_news_rss_url(query, lang=lang, country=country)
    feed = feedparser.parse(rss_url)
    # Filter entries by publication time (lookback_hours) and collect title/source/link
    filtered_entries = [
        {
            "title": entry.title,
            "source": entry.source,
            "link": entry.link,
        }
        for entry in feed.entries
        if dt.datetime.now() - dt.datetime(*entry.published_parsed[:6]) < dt.timedelta(hours=lookback_hours)
    ][:limit]
    print(filtered_entries)
    return filtered_entries
