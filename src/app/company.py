from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json
import time
import yfinance as yf

# TODO Create with 'Path' class the 'CACHE_FILE' object which stores location to 'company_cache.json'
# CACHE_FILE =

# TODO # Common legal suffixes often found in company names (ADD MORE),
# which we remove to get a cleaner keyword (e.g., "Apple Inc." -> "Apple"). 
LEGAL_SUFFIXES = {
    "inc", "inc.",
}

# TODO Add class attributes like in the class description

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
    pass

# TODO Finish this function:

def _load_cache() -> Dict[str, Any]:
    """Load cached company metadata from JSON file."""
    if CACHE_FILE.exists():
        try:
            # Return content of file
            pass
        except Exception:
            # Return empty dictionary
            pass
    else:
        # Return empty dictionary
        pass

def _save_cache(cache: Dict[str, Any]) -> None:
    """Save company metadata to local cache file."""
    # TODO What parameters are missing?
    # CACHE_FILE.write_text(json.dumps(), encoding="utf-8")


# TODO Finish the function logic    
def _strip_legal_suffixes(name: str) -> str:
    """
    Remove common legal suffixes from a company name.

    Example:
        "Apple Inc." -> "Apple"
        "SAP SE" -> "SAP"
    """
    parts = [p.strip(",. ") for p in name.split()]
    while parts and parts[-1].lower() in LEGAL_SUFFIXES:
        # There is something missing
        pass
    return " ".join(parts) if parts else name.strip()

# TODO Finish the function logic
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
        pass
    return symbol

# TODO Finish the try and except block
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
            # Missing code
            if info:
                return info
        except Exception as e:
            # Missing code
            time.sleep(delay)
    return {}


def get_company_meta(symbol: str) -> CompanyMeta:
    """
    Retrieve company metadata (name, base ticker, etc.) with caching and fallbacks.
    """
    # TODO: Load the cache with _load_cache() and return early if the symbol exists
    # cache = _load_cache()
    # if symbol in cache:
    #     ...

    # TODO: Fetch raw company information via _fetch_yf_info
    # info = _fetch_yf_info(symbol)

    # TODO: Extract a potential company name from info ("longName", "shortName", "displayName")
    # raw_name = ...
    # source = ...

    # TODO: Clean the extracted name with _strip_legal_suffixes and handle fallback to _base_ticker
    # clean = ...
    # if not clean:
    #     ...

    # TODO: Create a CompanyMeta instance and cache the result using _save_cache
    # meta = CompanyMeta(...)

    # TODO: Save the constructed metadata back into the cache
    # _save_cache(cache)

    pass  # Remove this once the function is implemented


def auto_keywords(symbol: str) -> Tuple[str, list[str]]:
    """
    Generate a company search keyword set based on symbol.
    """
    # TODO: Fetch the CompanyMeta for the symbol
    # meta = get_company_meta(symbol)

    # TODO: Determine the display name and construct the keyword list
    # name = ...
    # base = ...
    # primary = ...
    # req = ...

    # TODO: Return the cleaned name and the list of required keywords
    # return name, req

    pass  # Remove this once the function is implemented