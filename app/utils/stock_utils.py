import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_stock_info(ticker):
    """
    Get basic info for a stock
    
    Args:
        ticker (str): The stock ticker symbol
        
    Returns:
        dict: Dictionary with stock information or None if not found
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Basic validation to ensure we have real data
        if 'longName' not in info or info.get('quoteType', '').lower() != 'equity':
            return None
            
        # Return selected information
        return {
            'ticker': ticker.upper(),
            'name': info.get('longName', ''),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'volume': info.get('volume', 0),
            'average_volume': info.get('averageVolume', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'description': info.get('longBusinessSummary', '')
        }
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
        return None


def get_stock_historical_data(ticker, period='1mo'):
    """
    Get historical price data for a stock
    
    Args:
        ticker (str): The stock ticker symbol
        period (str): Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        list: List of dictionaries with date and price data
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return []
            
        # Convert dataframe to list of dicts for easier handling in Flask
        data = []
        for date, row in hist.iterrows():
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            })
            
        return data
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
        return []


def search_stocks(query):
    """
    Search for stocks by name or ticker
    This is a basic implementation. In a real app, you'd use a more robust search API.
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of matching stocks with basic info
    """
    try:
        # This is a simplified implementation. In a real app, you might use a proper API
        # Here we're just checking a few major stocks as an example
        common_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "BRK-B", "JPM", 
            "V", "PG", "JNJ", "UNH", "HD", "BAC", "XOM", "NVDA", "DIS", "ADBE"
        ]
        
        results = []
        query = query.upper()
        
        for ticker in common_tickers:
            if query in ticker:
                stock_info = get_stock_info(ticker)
                if stock_info:
                    results.append(stock_info)
                    
        return results
    except Exception as e:
        logger.error(f"Error searching stocks with query '{query}': {str(e)}")
        return []


def get_current_price(ticker):
    """
    Get just the current price for a stock
    
    Args:
        ticker (str): The stock ticker symbol
        
    Returns:
        float: Current stock price or 0 if error
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('currentPrice', stock.info.get('regularMarketPrice', 0))
    except Exception as e:
        logger.error(f"Error getting current price for {ticker}: {str(e)}")
        return 0


def get_market_summary():
    """
    Get summary of major market indices
    
    Returns:
        dict: Dictionary with market index data
    """
    try:
        # Use ETFs tracking these indices instead of direct index symbols
        # DIA for Dow Jones, SPY for S&P 500, QQQ for NASDAQ, IWM for Russell 2000
        indices = ["DIA", "SPY", "QQQ", "IWM"]
        names = ["Dow Jones (DIA)", "S&P 500 (SPY)", "NASDAQ (QQQ)", "Russell 2000 (IWM)"]
        
        result = []
        
        for i, index in enumerate(indices):
            ticker = yf.Ticker(index)
            hist = ticker.history(period="2d")
            
            if not hist.empty and len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                current = hist['Close'].iloc[-1]
                change = current - prev_close
                change_percent = (change / prev_close) * 100
                
                result.append({
                    'name': names[i],
                    'symbol': index,
                    'price': current,
                    'change': change,
                    'change_percent': change_percent
                })
                
        return result
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        return [] 