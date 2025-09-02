import datetime as dt
from zoneinfo import ZoneInfo
import logging
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import urlparse, parse_qs
import requests

from .market import get_open_and_last
from .ntfy import notify_ntfy
from .state import load_state, save_state
from .company import auto_keywords
from .news import fetch_headlines, build_query, filter_titles

logger = logging.getLogger("stock-alerts")


def _ticker_to_query(ticker: str, override_name: str | None = None) -> str:
    """
    Return a human-friendly query term for a ticker.

    Args:
        ticker: Raw ticker symbol (e.g., "AAPL").
        override_name: Optional override (e.g., "Apple").

    Returns:
        A display/query string; override_name if provided, else the ticker.
    """
    # TODO: Return override_name if provided; otherwise return ticker
    pass


def _ensure_https(u: str) -> str:
    """
    Ensure the given URL has a scheme. If missing, prefix with https://

    This helps when feeds provide bare domains or schemeless URLs.
    """
    # TODO: Handle empty strings
    # TODO: If u starts with http:// or https://, return u unchanged
    # TODO: Otherwise, prefix u with "https://"
    pass


def _extract_original_url(link: str, *, resolve_redirects: bool = True, timeout: float = 3.0) -> str:
    """
    Try to extract the original article URL from Google News redirect links.

    Strategy:
        1) If it's a news.google.com link and contains ?url=..., use that.
        2) Optionally resolve redirects via HEAD (fallback GET) to obtain the final URL.
        3) If all fails, return the input link.

    Args:
        link: Possibly a Google News RSS link.
        resolve_redirects: Whether to follow redirects to the final URL.
        timeout: Per-request timeout in seconds.

    Returns:
        A best-effort "clean" URL pointing to the original source.
    """
    # TODO: Normalize link via _ensure_https
    # TODO: If link is a news.google.com URL, attempt to extract ?url= parameter
    # TODO: Optionally resolve redirects via HEAD or GET
    # TODO: Return cleaned URL or fallback to original link
    pass


def _domain(url: str) -> str:
    """
    Extract a pretty domain (strip leading 'www.') from a URL for compact display.
    """
    # TODO: Parse the domain with urlparse
    # TODO: Strip leading "www." if present
    # TODO: Return cleaned domain or original url on error
    pass


def _format_headlines(items: List[Dict[str, Any]]) -> str:
    """
    Build a compact Markdown block for headlines.

    - Web (ntfy web app): Markdown will be rendered (nice links)
    - Mobile (ntfy apps): Markdown shows as plain text, so we also include
      a short, real URL line that remains clickable on phones.

    Returns:
        A multi-line string ready to embed into the notification body.
    """
    # TODO: Handle empty list case
    # TODO: Build Markdown lines with titles, sources and cleaned links
    # TODO: Join lines with newline characters and return the result
    pass


def now_tz(tz: str) -> dt.datetime:
    """
    Get current date/time in a specific timezone (e.g., 'Europe/Berlin').

    Using timezone-aware datetimes avoids DST pitfalls and makes logging consistent.
    """
    # TODO: Use dt.datetime.now with ZoneInfo to return timezone-aware datetime
    pass


def is_market_hours(cfg_mh: dict) -> bool:
    """
    Heuristic market-hours check (simple window, no holidays).

    Args:
        cfg_mh: Market hours config with keys:
            - enabled (bool)
            - tz (str)
            - start_hour (int)
            - end_hour (int)
            - days_mon_to_fri_only (bool)

    Returns:
        True if within the configured hours, else False.
    """
    # TODO: If checking is disabled, return True
    # TODO: Obtain current time via now_tz(cfg_mh["tz"])
    # TODO: Optionally limit to Monday–Friday
    # TODO: Compare current hour with start_hour/end_hour
    pass


def run_once(
    tickers: List[str],
    threshold_pct: float,
    ntfy_server: str,
    ntfy_topic: str,
    state_file: Path,
    market_hours_cfg: dict,
    test_cfg: dict,
    news_cfg: dict,
) -> None:
    """
    Execute one monitoring cycle:
      - Check market hours (with optional test bypass)
      - For each ticker:
          * Fetch open & last price (intraday preferred)
          * Compute Δ% vs. open
          * Trigger ntfy push if |Δ%| ≥ threshold (with de-bounce via state file)
          * Optionally attach compact news headlines (with cleaned source URLs)

    Side effects:
      - Sends an HTTP POST to ntfy (unless dry_run)
      - Reads/writes the alert state JSON (anti-spam)
      - Writes logs according to logging setup
    """
    # TODO: Log job start and determine market-hours eligibility
    # TODO: Load alert state from state_file
    # TODO: Iterate over tickers and fetch open/last prices
    # TODO: Compute Δ% and apply test overrides if needed
    # TODO: Decide whether to send alerts and prepare notification body
    # TODO: Optionally fetch and format news headlines
    # TODO: Send notification via notify_ntfy and persist state via save_state
    pass
