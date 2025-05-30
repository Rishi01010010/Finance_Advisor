import requests
from bs4 import BeautifulSoup

def get_earnings_surprise(ticker: str):
    url = f"https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    tables = soup.find_all('table')
    for table in tables:
        if "Earnings Estimate" in table.text:
            rows = table.find_all("tr")
            data = [row.text for row in rows if "Avg. Estimate" in row.text]
            return {"ticker": ticker, "surprise_info": data}

    return {"ticker": ticker, "surprise_info": "Not found"}