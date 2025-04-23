from django.core.management.base import BaseCommand
import yfinance as yf
import mysql.connector
import numpy as np
import pandas as pd

def fetch_historical_data(ticker, period="30d"):  # Default to "30d" if no period is specified
    stock = yf.Ticker(ticker)
    historical_data = stock.history(period=period)  # Use the 'period' argument here
    return historical_data

def calculate_return_rate(data):
    if len(data) < 2:
        return 0.0
    today_close = data.iloc[-1]['Close']
    yesterday_close = data.iloc[-2]['Close']
    return float((today_close - yesterday_close) / yesterday_close)

def calculate_volatility(data):
    data['Daily Return'] = data['Close'].pct_change()
    return float(data['Daily Return'].std())


class Command(BaseCommand):
    help = 'Fetches 30-day stock data and inserts latest data with return rate and volatility into the COMPANY_STOCK table'

    def handle(self, *args, **kwargs):
        tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS',  'KOTAKBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'HCLTECH.NS', 'ITC.NS', 'M&M.NS', 'ULTRACEMCO.NS', 'MARUTI.NS', 'NTPC.NS', 'ASIANPAINT.NS', 'BAJFINANCE.NS', 'HINDUNILVR.NS', 'WIPRO.NS', 'BPCL.NS', 'SUNPHARMA.NS', 'TECHM.NS', 'HDFCLIFE.NS', 'TITAN.NS', 'POWERGRID.NS', 'DIVISLAB.NS', 'ADANIGREEN.NS', 'TATAMOTORS.NS', 'ONGC.NS', 'INDUSINDBK.NS', 'CIPLA.NS', 'SHREECEM.NS', 'MOTHERSON.NS', 'HEROMOTOCO.NS', 'DRREDDY.NS', 'JSWSTEEL.NS', 'AXISBANK.NS', 'EICHERMOT.NS', 'APOLLOHOSP.NS', 'MARICO.NS', 'GRASIM.NS', 'NESTLEIND.NS', 'RELIANCE.NS', 'ADANIPORTS.NS', 'VEDL.NS', 'M&MFIN.NS', 'HINDALCO.NS', 'GAIL.NS', 'TECHM.NS']  
        
        for ticker in tickers:
            historical_data = fetch_historical_data(ticker, period="30d")
            
            if not historical_data.empty:
                # Calculate return rate and volatility
                return_rate = calculate_return_rate(historical_data)
                volatility = calculate_volatility(historical_data)
                if pd.isna(volatility):
                    volatility = 0.0

                latest_row = historical_data.iloc[-1]  # Get the latest row (last available data)
                stock_data = {
                    'date': latest_row.name.date().isoformat(),
                    'open': float(latest_row['Open']),
                    'close': float(latest_row['Close']),
                    'high': float(latest_row['High']),
                    'low': float(latest_row['Low']),
                    'price': float(latest_row['Close'])  # Using close as the current price
                }

                try:
                    # Establish connection to MySQL
                    connection = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="S1tty1$great",
                        database="stock"
                    )
                    cursor = connection.cursor()

                    # Insert stock data into COMPANY_STOCK table
                    cursor.execute("""
                        INSERT INTO COMPANY_STOCK (COMPANY_ID, CNAME, OPENRATE, CLOSERATE, DAYHIGH, DAYLOW, PRICE, CURRDATE, RETURNRATE, VOLATILITY)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        ticker, ticker, stock_data['open'], stock_data['close'],
                        stock_data['high'], stock_data['low'], stock_data['price'],
                        stock_data['date'], return_rate, volatility
                    ))

                    # Commit the transaction
                    connection.commit()

                    # Success message
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully inserted stock data for {ticker} with return rate and volatility."))

                except mysql.connector.Error as err:
                    # Error message
                    self.stdout.write(self.style.ERROR(f"❌ MySQL Error: {err}"))

                finally:
                    # Ensure that the connection is closed
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
                    else:
                        self.stdout.write(self.style.ERROR(f"❌ Failed to close MySQL connection properly for {ticker}"))
            else:
                # If no historical data is found
                self.stdout.write(self.style.ERROR(f"❌ No historical data found for {ticker}"))      
