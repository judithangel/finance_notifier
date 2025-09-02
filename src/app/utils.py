def mask_secret(s: str, keep: int = 1) -> str:
    """Maskiert sensible Strings für Logging-Ausgaben."""
    # Gib "(unset)" zurück, falls der String leer oder None ist
    if not s:
        return "(unset)"
    # Falls die Länge > keep * 2 ist, behalte jeweils die ersten/letzten
    # Andernfalls gib den ersten und letzten Buchstaben mit Ellipse dazwischen aus
    return s[:keep] + "..." + s[-keep:]
