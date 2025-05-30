import yfinance as yf

def load_market_data(ticker: str):
    ticker_obj = yf.Ticker(ticker)
    return ticker_obj.history(period="5d")