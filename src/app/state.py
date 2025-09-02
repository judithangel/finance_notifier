import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger("stock-alerts")


def load_state(path: Path) -> Dict[str, str]:
    """
    Load the last alert "state" from a JSON file.

    The state keeps track of which direction (up/down/none) a stock
    has already triggered an alert for. This prevents sending duplicate
    notifications every run.
    """
    # Prüfen, ob die Datei existiert und deren Inhalt als JSON laden
    if not path.exists():
        logger.warning("State file does not exist, returning empty state")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
            logger.debug("Loaded state: %s", state)
            return state
    except Exception as e:
        logger.warning("Failed to load state: %s", e)
        return {}


def save_state(path: Path, state: Dict[str, str]) -> None:
    """
    Save the current alert state to disk.
    """
    # Den Zustand als JSON (UTF-8) in die Datei schreiben
    path.write_text(json.dumps(state), encoding="utf-8")
    logger.debug("Saved state: %s", state)
