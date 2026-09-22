import asyncio 
import httpx
import os

from src.parser import extract_stock_data
from src.scraper import StockScraper
from src.models import PharmaMetricSchema
from src.database import DataBaseManager

TICKERS = ["lly", "jnj", "abbv", "mrk", "nvs", "azn", "amgn", "nvo", "gild", "pfe"]

async def process_ticker(scraper, client, ticker):
    html = await scraper.fetch_html(client, ticker)
    if html is None:
        return None

    return extract_stock_data(html, ticker)

async def run_pipeline():
    scraper = StockScraper()
    db = DataBaseManager(os.getenv("DATABASE_URL", "sqlite:///pharma_pipeline.db"))
    valid_records: list[PharmaMetricSchema] = []

    print(f"Iniciando extraccion para {len(TICKERS)} companias...")

    async with httpx.AsyncClient() as client:
        tasks = [process_ticker(scraper, client, ticker) for ticker in TICKERS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for ticker, res in zip(TICKERS, results):
            if isinstance(res, Exception) or res is None:
                print(f"[WARN] No se pudo obtener datos para {ticker}")
                continue

            try: 
                record = PharmaMetricSchema.model_validate(res)
                valid_records.append(record)
            except Exception as e:
                print(f"[ERR] Fallo el parseo/validacion para {ticker}: {e}")

        saved_count = db.save_or_update_metrics(valid_records)
        print(f"Pipeline completado: {saved_count} registros guardados.")

        db.print_all_metrics()

if __name__ == "__main__":
    data = asyncio.run(run_pipeline())