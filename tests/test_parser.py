import pytest
from src.parser import parse_numeric_suffix, parse_percentage, extract_stock_data

def test_parse_numeric_suffix_multipliers():
    """
    Test 1: Verifica normalizacion de magnitudes (T, B, M).
    Comprueba que strings con simbolos de moneda y sufijos se transformen correctamente
    en valores de tipo float
    """
    assert parse_numeric_suffix("$1.03T") == 1.03e12
    assert parse_numeric_suffix("$342.42B") == 342.42e9
    assert parse_numeric_suffix("32.5M") == 32.5e6
    assert parse_numeric_suffix("$54.00") == 54.00
    assert parse_numeric_suffix("invalid_input") is None

def test_null_vs_zero_differentiation():
    """
    Test 2: Verifica el manejo de valores faltantes frente a valores numericos reales.
    Comprueba que cadenas como 'n/a', '-' o vacios se normalicen a None mientras que 
    '0.0%' y '+0.0%' se preserven como 0.0 float.
    """

    assert parse_numeric_suffix("-") is None
    assert parse_numeric_suffix("n/a") is None
    assert parse_percentage("-") is None
    assert parse_percentage("n/a") is None
    assert parse_percentage("") is None

    assert parse_percentage("0.0%") == 0.0
    assert parse_percentage("+0.00%") == 0.0
    assert parse_percentage("-0.00%") == 0.0

def test_extract_stock_data_sample_html():
    """
    Test 3: Verifica la extraccion de campos desde un fixture HTML sin interaccion de red.
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