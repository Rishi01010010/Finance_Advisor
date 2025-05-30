# from fastapi import FastAPI, Query
# import requests
# import yfinance as yf
# import os
# from dotenv import load_dotenv

# load_dotenv()
# ALPHA_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# app = FastAPI()

# @app.get("/market_data")
# def get_market_data(ticker: str = Query(...)):
#     yf_data = yf.Ticker(ticker)
#     hist = yf_data.history(period="1d")
#     current_price = hist['Close'].iloc[-1] if not hist.empty else None
#     change_pct = ((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100 if not hist.empty else None

#     alpha_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_KEY}"
#     res = requests.get(alpha_url).json()

#     return {
#         "ticker": ticker,
#         "current_price": current_price,
#         "change_pct": change_pct,
#         "sector": res.get("Sector"),
#         "market_cap": res.get("MarketCapitalization")
#     }


from fastapi import FastAPI, Query
import requests
import yfinance as yf
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

app = FastAPI()

@app.get("/market_data")
def get_market_data(ticker: str = Query(...)):
    try:
        # Get Yahoo Finance data
        yf_data = yf.Ticker(ticker)
        hist = yf_data.history(period="1d")
        
        current_price = None
        change_pct = None
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            if len(hist) > 0:
                open_price = hist['Open'].iloc[-1]
                change_pct = ((current_price - open_price) / open_price) * 100

        # Get Alpha Vantage data if API key is available
        sector = None
        market_cap = None
        
        if ALPHA_KEY:
            try:
                alpha_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_KEY}"
                res = requests.get(alpha_url, timeout=10)
                alpha_data = res.json()
                sector = alpha_data.get("Sector")
                market_cap = alpha_data.get("MarketCapitalization")
            except Exception as e:
                logger.warning(f"Alpha Vantage API error: {e}")

        return {
            "ticker": ticker,
            "current_price": current_price,
            "change_pct": change_pct,
            "sector": sector,
            "market_cap": market_cap
        }
        
    except Exception as e:
        logger.error(f"Error getting market data for {ticker}: {e}")
        return {
            "ticker": ticker,
            "current_price": None,
            "change_pct": None,
            "sector": None,
            "market_cap": None,
            "error": str(e)
        }