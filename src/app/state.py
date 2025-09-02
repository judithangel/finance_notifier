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
    # TODO: Prüfen, ob die Datei existiert und deren Inhalt als JSON laden
    # TODO: Bei Erfolg den geladenen Zustand zurückgeben und einen Debug-Log schreiben
    # TODO: Bei Fehlern eine Warnung loggen und ein leeres Dict zurückgeben
    pass


def save_state(path: Path, state: Dict[str, str]) -> None:
    """
    Save the current alert state to disk.
    """
    # TODO: Den Zustand als JSON (UTF-8) in die Datei schreiben
    # TODO: Einen Debug-Log mit dem gespeicherten Zustand ausgeben
    pass
