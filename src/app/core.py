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
    if override_name:
        return override_name
    return ticker


def _ensure_https(u: str) -> str:
    """
    Ensure the given URL has a scheme. If missing, prefix with https://

    This helps when feeds provide bare domains or schemeless URLs.
    """
    # Handle empty strings
    if u == "":
        raise ValueError("URL is empty")
    # If u starts with http:// or https://, return u unchanged
    if u.startswith(("http://", "https://")):
        return u
    else:
        # Otherwise, prefix u with "https://"
        u = "https://" + u
    return u


# TODO: Where to use this function?
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
    # Normalize link via _ensure_https
    link = _ensure_https(link)
    # If link is a news.google.com URL, attempt to extract ?url= parameter
    if link.startswith("https://news.google.com"):
        try:
            url = link.split("?url=")[1].split("&")[0]
        except Exception as e:
           logger.warning("Failed to extract original URL from Google News link: %s", e) 
    # Optionally resolve redirects via HEAD or GET
    if resolve_redirects:
        try:
            resp = requests.head(link, allow_redirects=True, timeout=timeout)
            if resp.status_code == 200:
                url = resp.url
            else:
                resp = requests.get(link, allow_redirects=True, timeout=timeout)
                if resp.status_code == 200:
                    url = resp.url
        except Exception as e:
            logger.warning("Failed to resolve redirects for link %s: %s", link, e)
    # Return cleaned URL or fallback to original link
    return url if url else link


def _domain(url: str) -> str:
    """
    Extract a pretty domain (strip leading 'www.') from a URL for compact display.
    """
    # Parse the domain with urlparse
    try:
        parse_res = urlparse(url)
        domain = parse_res.hostname
        # Strip leading "www." if present
        if domain.startswith("www."):
            domain = domain.lstrip("www.")
    except Exception:
        logger.warning(f"Failed to parse domain from URL {url}")
        return url

    # Return cleaned domain or original url on error
    return domain


def _format_headlines(items: List[Dict[str, Any]]) -> str:
    """
    Build a compact Markdown block for headlines.

    - Web (ntfy web app): Markdown will be rendered (nice links)
    - Mobile (ntfy apps): Markdown shows as plain text, so we also include
      a short, real URL line that remains clickable on phones.

    Returns:
        A multi-line string ready to embed into the notification body.
    """
    # Handle empty list case
    if items == []:
        logger.warning(" No headlines to format")
        return ""
    # Build Markdown lines with titles, sources and cleaned links
    headlines = []
    for item in items:
        headline = f"- {item['title']} -  {_domain(item['link'])}\n 🔗 {item['link']}"
        headlines.append(headline)
    # Join lines with newline characters and return the result
    return "\n".join(headlines)


def now_tz(tz: str) -> dt.datetime:
    """
    Get current date/time in a specific timezone (e.g., 'Europe/Berlin').

    Using timezone-aware datetimes avoids DST pitfalls and makes logging consistent.
    """
    # Use dt.datetime.now with ZoneInfo to return timezone-aware datetime
    timezone = ZoneInfo(tz)
    return dt.datetime.now(timezone)


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
    # If checking is disabled, return True
    if not cfg_mh["enabled"]:
        return True
    # Obtain current time via now_tz(cfg_mh["tz"])
    time_now = now_tz(cfg_mh["tz"])

    # Limit to Monday–Friday
    if time_now.weekday() >= 5:
        return False
    
    # Compare current hour with start_hour/end_hour
    if not (cfg_mh["start_hour"] <= time_now.hour < cfg_mh["end_hour"]):
        return False
    return True


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
    # Log job start and determine market-hours eligibility
    logging.info("Starting monitoring cycle")
    if not is_market_hours(market_hours_cfg):
        if test_cfg.get("bypass_market_hours", False):
            logging.warning("Outside market hours, but bypass enabled via test config")
        else:
            logging.info("Outside market hours, skipping monitoring cycle")
            return
    # Load alert state from state_file
    state = load_state(state_file)
    # Iterate over tickers and fetch open/last prices
    for ticker in tickers:
        price_open, price_last = get_open_and_last(ticker)
        # Compute Δ% and apply test overrides if needed
        delta_pct = (price_last - price_open) / price_open * 100 if price_open else 0
        # TODO: Test overrides?
        # Decide whether to send alerts and prepare notification body
        if abs(delta_pct) >= threshold_pct:
            name, req = auto_keywords(ticker)
            symbol = req[1]
            state[ticker] = {"last_price": price_last, "open_price": price_open, "alerted": True}
            stock_info = f"📈  {symbol}: {delta_pct}% vs. Open\nAktuell: {price_last:.2f} | Open: {price_open:.2f}\n"
            # Optionally fetch and format news headlines
            if news_cfg["enabled"]:
                items = fetch_headlines(
                    query=build_query(name=ticker, ticker=ticker),
                    limit=news_cfg["limit"],
                    lookback_hours=news_cfg["lookback_hours"],
                    lang=news_cfg["lang"],
                    country=news_cfg["country"],
                )
                headlines = _format_headlines(
                    filter_titles(items, required_keywords=req)
                )
                # Join stock_info and headlines
                message = "\n".join([stock_info, headlines])
            else:
                message = stock_info
            # Send notification via notify_ntfy and persist state via save_state
            notify_ntfy(
                server=ntfy_server,
                topic=ntfy_topic,
                title=f"Stock Alert: {symbol}",
                message=message
            )
        else:
            state[ticker] = {"last_price": price_last, "open_price": price_open, "alerted": False}
        
        save_state(state_file, state)
    pass
