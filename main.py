import asyncio 
import httpx
from src.parser import extract_stock_data
from src.scraper import StockScraper

TICKERS = ["lly", "jnj", "abbv", "mrk", "nvs", "azn", "amgn", "nvo", "gild", "pfe"]

async def process_ticker(scraper, client, ticker):
    html = await scraper.fetch_html(client, ticker)
    if html is None:
        return None

    return extract_stock_data(html, ticker)

async def run_pipeline():
    scraper = StockScraper()

    async with httpx.AsyncClient() as client:
        tasks = [process_ticker(scraper, client, ticker) for ticker in TICKERS]
        results = await asyncio.gather(*tasks)

    valid_records = [r for r in results if r is not None]
    print(f"Extracción finalizada: {len(valid_records)}/{len(TICKERS)} procesados exitosamente.")

    return valid_records

if __name__ == "__main__":
    data = asyncio.run(run_pipeline())
    for item in data:
        print(item)