import asyncio
import httpx

class StockScraper:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(2)
        self.base_url = "https://stockanalysis.com/stocks/{ticker}/statistics/"

    async def fetch_html(self, client: httpx.AsyncClient, ticker):
        url = self.base_url.format(ticker=ticker.lower())

        async with self.semaphore:
            try:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            
            except httpx.HTTPError as err:
                print(f"[{ticker.upper()}] Error al descargar: {err}")
                return None