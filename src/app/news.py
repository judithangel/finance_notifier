from __future__ import annotations
import datetime as dt
from typing import List, Dict, Iterable
from urllib.parse import quote_plus
import feedparser


def build_query(name: str, ticker: str) -> str:
    """
    Build a Google News search query for a company.
    """
    # TODO: Return a query combining company name, ticker, and finance keywords
    pass


def filter_titles(items: List[Dict[str, str]], required_keywords: Iterable[str] = ()) -> List[Dict[str, str]]:
    """
    Filter news items so that only those containing required keywords
    in their title are kept.
    """
    # TODO: If no required keywords, return items unchanged
    # TODO: Otherwise, keep only items whose title contains any keyword (case-insensitive)
    pass


def _google_news_rss_url(query: str, lang: str = "de", country: str = "DE") -> str:
    """
    Build a Google News RSS URL for a given query.
    """
    # TODO: Encode the query with quote_plus, append "when:12h"
    # TODO: Construct and return the final RSS URL
    pass


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
    # TODO: Build the RSS URL via _google_news_rss_url and parse it with feedparser
    # TODO: Filter entries by publication time (lookback_hours) and collect title/source/link
    # TODO: Stop after collecting 'limit' items
    pass
