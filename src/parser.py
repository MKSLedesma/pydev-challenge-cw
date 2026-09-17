from typing import Optional
from bs4 import BeautifulSoup

NULL_REPRESENTATIONS = {"-", "n/a", ""}

def parse_numeric_suffix(val: Optional[str]) -> Optional[float]:
    """ 
    Normaliza strings con sufijos (B, T, M) a float.

    Diferencia entre None y 0.
    """
    multipliers = {
        "T": 1e12,
        "B": 1e9,
        "M": 1e6,
    }

    if val is None:
        return None

    clean = val.replace("$", "").replace(",", "").strip()
    if clean in NULL_REPRESENTATIONS:
        return None

    last_char = clean[-1] if clean else ""

    if last_char in multipliers:
        multiplier = multipliers[last_char]
        clean = clean[:-1]
    else:
        multiplier = 1.0

    try:
        return float(clean) * multiplier
    except ValueError:
        return None

def parse_percentage(val: Optional[str]) -> Optional[float]:
    """ 
    Normaliza strings de porcentaje a float.

    Diferencia 'n/a' de '0.0%'.
    """
    if val is None:
        return None

    clean = val.replace("%", "").replace("+", "").strip()
    if clean in NULL_REPRESENTATIONS:
        return None

    try:
        return float(clean)
    except ValueError:
        return None

