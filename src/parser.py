from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

NULL_REPRESENTATIONS = {"-", "n/a", ""}

MULTIPLIERS = {
    "T": 1e12,
    "B": 1e9,
    "M": 1e6,
}

def parse_numeric_suffix(val: Optional[str]) -> Optional[float]:
    """ 
    Normaliza strings con sufijos (B, T, M) a float.

    Diferencia entre None y 0.
    """

    if val is None:
        return None

    clean = val.replace("$", "").replace(",", "").strip()
    if clean in NULL_REPRESENTATIONS:
        return None

    last_char = clean[-1] if clean else ""
    if last_char in MULTIPLIERS:
        multiplier = MULTIPLIERS[last_char]
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

def get_metric_value(soup, label):
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2:
            cell_label = tds[0].get_text(strip=True)
            if cell_label.lower() == label.lower():
                return tds[1].get_text(strip=True)
    return None

def extract_stock_data(html: str, ticker: str) -> Dict[str, Any]:
    """Parsea el HTML de /stadistics/ por ticker y extrae los campos definidos."""
    soup = BeautifulSoup(html, "html.parser")

    # 1. Nombre de la compania
    name_elem = soup.find("div", class_=lambda c: c and "font_bold" in c and "text-2xl" in c)
    raw_name = name_elem.get_text(strip=True) if name_elem else ticker.upper()
    if " (" in raw_name and raw_name.endswith(")"):
        company_name = raw_name.rsplit(" (", 1)[0].strip()
    else:
        company_name = raw_name

    # 2. Precio de la accion
    price_elem = soup.find("div", class_=lambda c: c and "text-4xl" in c)
    main_share_price = None
    if price_elem:
        raw_price = price_elem.get_text(strip=True).replace("$", "").replace(",", "")
        try:
            main_share_price = float(raw_price)
        except ValueError:
            main_share_price = None

    # 3. Moneda 
    currency = "USD"
    meta_elem = soup.find("div", class_=lambda c: c and "text-tiny" in c and "text-faded" in c)
    if meta_elem:
        meta_text = meta_elem.get_text(strip=True)
        if "·" in meta_text:
            currency = meta_text.rsplit("·", 1)[-1].strip()

    # 4. Metricas dentro de tablas
    market_cap = parse_numeric_suffix(get_metric_value(soup, "Market Cap"))
    week_52_change = parse_percentage(get_metric_value(soup, "52-Week Price Change"))

    return {"company": company_name,
            "ticker": ticker.upper(),
            "main_share_price": main_share_price,
            "currency": currency,
            "market_cap": market_cap,
            "week_52_price_change": week_52_change,
            "extracted_at_utc": datetime.now(timezone.utc)
        }