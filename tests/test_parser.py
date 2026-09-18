import pytest

from datetime import datetime, timezone
from src.parser import parse_numeric_suffix, parse_percentage, extract_stock_data
from src.database import DataBaseManager
from src.models import PharmaMetricSchema

def test_numeric_and_null_normalization():
    """
    Test 1: Verifica normalizacion de magnitudes (T, B, M) y manejo de valores nulos vs. cero.
    Comprueba que strings con simbolos de moneda y sufijos se transformen correctamente
    en valores de tipo float, que indicadores visuales nulos ('n/a', '-') devuelvan None
    y que '0.0%' se preserve como 0.0 numerico.
    """
    # 1. Multiplicadores
    assert parse_numeric_suffix("$1.03T") == 1.03e12
    assert parse_numeric_suffix("$342.42B") == 342.42e9
    assert parse_numeric_suffix("32.5M") == 32.5e6
    assert parse_numeric_suffix("$54.00") == 54.00
    assert parse_numeric_suffix("invalid_input") is None

    # 2. Valores faltantes
    assert parse_numeric_suffix("-") is None
    assert parse_numeric_suffix("n/a") is None
    assert parse_percentage("-") is None
    assert parse_percentage("n/a") is None
    assert parse_percentage("") is None

    # 3. Cero real
    assert parse_percentage("0.0%") == 0.0
    assert parse_percentage("+0.00%") == 0.0
    assert parse_percentage("-0.00%") == 0.0

def test_extract_stock_data_sample_html():
    """
    Test 2: Verifica la extraccion de campos desde un fixture HTML sin interaccion de red.
    Comprueba que se limpien parentesis del nombre del laboratorio, se detecte la divisa,
    se extraiga el precio y se mappen las metricas en tablas.
    """
    sample_html = """
    <div>
        <div class="mb-0 text-2xl font-bold">Eli Lilly and Company (LLY)</div>
        <div class="mt-[1px] text-tiny text-faded">NYSE: LLY · Real-Time Price · USD</div>
        <div class="text-4xl font-bold">$950.50</div>
        <table>
            <tbody>
                <tr>
                    <td><a href="/stocks/lly/market-cap/">Market Cap</a></td>
                    <td>1.03T</td>
                </tr>
                <tr>
                    <td><span>52-Week Price Change</span></td>
                    <td>+45.20%</td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    data = extract_stock_data(sample_html, ticker="LLY")

    assert data["company"] == "Eli Lilly and Company"
    assert data["ticker"] == "LLY"
    assert data["currency"] == "USD"
    assert data["main_share_price"] == 950.50
    assert data["market_cap"] == 1.03e12
    assert data["week_52_price_change"] == 45.20
    assert data["extracted_at_utc"] is not None

def test_database_insert():
    """
    Test 3: Verifica la persistencia de INSERT usando SQLite en memoria.
    Comprueba que reinsertar el mismo laboratorio actualiza el registro existente.
    """
    db = DataBaseManager(db_url="sqlite:///:memory:")

    record_initial = PharmaMetricSchema(
        company="Eli Lilly and Company",
        ticker="LLY",
        main_share_price=900.00,
        currency="USD",
        market_cap=1.00e12,
        week_52_price_change=67.00,
        extracted_at_utc=datetime.now(timezone.utc)
    )

    inserted = db.save_or_update_metrics([record_initial])
    assert inserted == 1

    records = db.get_all_metrics()
    assert len(records) == 1
    assert records[0].main_share_price == 900.00

    record_updated = PharmaMetricSchema(
        company="Eli Lilly and Company",
        ticker="LLY",
        main_share_price=925.30,
        currency="USD",
        market_cap=1.03e12,
        week_52_price_change=75.00,
        extracted_at_utc=datetime.now(timezone.utc)
    )

    updated = db.save_or_update_metrics([record_updated])
    assert updated == 1

    final_records = db.get_all_metrics()
    assert len(final_records) == 1
    assert final_records[0].main_share_price == 925.30
    assert final_records[0].market_cap == 1.03e12
    assert final_records[0].week_52_price_change == 75.00