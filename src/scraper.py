import asyncio
import httpx
from bs4 import BeautifulSoup

class StockScraper:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(2)
        self.base_url = "https://stockanalysis.com/stocks/{ticker}/statistics/"

    async def fetch_and_find_tables(self, client: httpx.AsyncClient, ticker):
        url = self.base_url.format(ticker=ticker.lower())

        async with self.semaphore:
            try:
                response = await client.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                tables = soup.find_all("table")

                print(f"[{ticker.upper()}] Status {response.status_code} - Tablas encontradas: {len(tables)}")

                return tables

            except httpx.HTTPError as err:
                print(f"[{ticker.upper()}] Error al descargar: {err}")
                return None

async def main():
    tickers = ["lly", "jnj", "abbv", "mrk", "nvs", "azn", "amgn", "nvo", "gild", "pfe"]

    async with httpx.AsyncClient() as client:
        tasks = [
            StockScraper().fetch_and_find_tables(client, ticker)
            for ticker in tickers
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())