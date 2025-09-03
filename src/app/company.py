from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json
import time
import yfinance as yf
import logging

# Create with 'Path' class the 'CACHE_FILE' object which stores location to 'company_cache.json'
CACHE_FILE = Path("company_cache.json")

# Common legal suffixes often found in company names,
# which we remove to get a cleaner keyword (e.g., "Apple Inc." -> "Apple"). 
LEGAL_SUFFIXES = {
    "inc", "GmbH", "AG", "Ltd", "LLC", "Corp", "Co", "PLC", "SE"
}

logger = logging.getLogger("stock-alerts")


@dataclass
class CompanyMeta:
    """
    Represents metadata about a company/ticker.
    
    Attributes:
        ticker (str): The full ticker symbol, e.g., "SAP.DE".
        name (Optional[str]): Cleaned company name without legal suffixes, e.g., "Apple".
        raw_name (Optional[str]): Original company name as returned by Yahoo Finance, e.g., "Apple Inc.".
        source (str): Source of the name (e.g., "info.longName", "info.shortName", "fallback").
        base_ticker (str): Simplified ticker without suffixes, e.g., "SAP" for "SAP.DE".
    """
    ticker: str
    name: Optional[str]
    raw_name: Optional[str]
    source: str
    base_ticker: str


def _load_cache() -> Dict[str, Any]:
    """Load cached company metadata from JSON file."""
    if CACHE_FILE.exists():
        try:
            metadata = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            return metadata
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}
    else:
        # Return empty dictionary
        return {}

def _save_cache(cache: Dict[str, Any]) -> None:
    """Save company metadata to local cache file."""
    CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")

def _strip_legal_suffixes(name: str) -> str:
    """
    Remove common legal suffixes from a company name.

    Example:
        "Apple Inc." -> "Apple"
        "SAP SE" -> "SAP"
    """
    if not name:
        return None
    parts = [p.strip(",. ") for p in name.split()]
    while parts and parts[-1].lower() in LEGAL_SUFFIXES:
        parts = parts[:-1]
    return " ".join(parts) if parts else name.strip()

def _base_ticker(symbol: str) -> str:
    """
    Extract the base ticker symbol.

    Examples:
        "SAP.DE" -> "SAP"
        "BRK.B"  -> "BRK"
        "^GDAXI" -> "^GDAXI" (indices remain unchanged)
    """
    if symbol.startswith("^"):  # Index tickers like ^GDAXI
        pass
    if "." in symbol:
        symbol = symbol.split(".")[0]
    return symbol

def _fetch_yf_info(symbol: str, retries: int = 2, delay: float = 0.4) -> Dict[str, Any]:
    """
    Fetch company information from Yahoo Finance.

    Args:
        symbol (str): Ticker symbol.
        retries (int): Number of retries if request fails.
        delay (float): Delay between retries in seconds.

    Returns:
        dict: Yahoo Finance info dictionary (may be empty if lookup fails).
    """
    last_exc = None
    for _ in range(retries + 1):
        try:
            info = yf.Ticker(symbol).info
            if info:
                return info
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    logger.error(f"Failed to fetch Yahoo Finance info for {symbol}: {last_exc}")
    return {}


def get_company_meta(symbol: str) -> CompanyMeta:
    """
    Retrieve company metadata (name, base ticker, etc.) with caching and fallbacks.
    """
    # Load the cache with _load_cache() and return early if the symbol exists
    cache = _load_cache()

    # Fetch raw company information via _fetch_yf_info
    info = _fetch_yf_info(symbol)

    # Extract a potential company name from info ("longName", "shortName", "displayName")
    sources = ["longName", "shortName", "displayName"]
    for s in sources:
        if info.get(s):
            raw_name = info.get(s)
            source = s
            break
    else:
        raw_name = None
        source = "fallback"

    # Clean the extracted name with _strip_legal_suffixes and handle fallback to _base_ticker
    clean = _strip_legal_suffixes(raw_name)
    if not clean:
        clean = _base_ticker(symbol)

    # Create a CompanyMeta instance and cache the result using _save_cache
    meta = CompanyMeta(ticker=symbol, name=clean, raw_name=raw_name, source=source,
                       base_ticker=_base_ticker(symbol))
    meta_dict = meta.__dict__

    # Save the constructed metadata back into the cache
    _save_cache(meta_dict)

    return meta

def auto_keywords(symbol: str) -> Tuple[str, list[str]]:
    """
    Generate a company search keyword set based on symbol.
    """
    # Fetch the CompanyMeta for the symbol
    meta = get_company_meta(symbol)

    # Determine the display name and construct the keyword list
    try:
        name = meta.name
    except AttributeError:
        name = meta.ticker
    base = meta.base_ticker
    primary = meta.raw_name
    req = [name, base, primary, primary.strip(".")]

    # Return the cleaned name and the list of required keywords
    return name, req