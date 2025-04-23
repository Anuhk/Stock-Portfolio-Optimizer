# utils.py
import yfinance as yf
import numpy as np
import pandas as pd

def fetch_returns_and_covariance(tickers, period="30d"):
    data = yf.download(tickers, period=period)['Close']

    if isinstance(data, pd.Series):
        data = data.to_frame()

    daily_returns = data.pct_change().dropna()
    mean_returns = daily_returns.mean()
    cov_matrix = daily_returns.cov()

    return mean_returns.values, cov_matrix.values, list(daily_returns.columns)

def fetch_stock_data(ticker):
    import yfinance as yf

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")

    if hist.empty:
        return None

    latest = hist.iloc[-1]
    return {
        'ticker': ticker,
        'open': round(latest['Open'], 2),
        'close': round(latest['Close'], 2),
        'high': round(latest['High'], 2),
        'low': round(latest['Low'], 2),
        'price': round(latest['Close'], 2),
        'date': latest.name.strftime('%Y-%m-%d'),
    }
