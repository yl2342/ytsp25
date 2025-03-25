"""
API endpoints for stock data in the Yale Trading Simulation Platform.
Provides routes for retrieving stock information, historical data, and search functionality.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.utils.stock_utils import get_stock_info, get_stock_historical_data, search_stocks, get_market_summary
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint for stock API endpoints
stock_api_bp = Blueprint('stock_api', __name__)

@stock_api_bp.route('/stock/info/<ticker>', methods=['GET'])
@login_required
def api_stock_info(ticker):
    """
    Get basic information about a stock.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON response with stock information or error message
    """
    ticker = ticker.upper()
    stock_info = get_stock_info(ticker)
    
    if stock_info:
        return jsonify({
            'success': True,
            'data': stock_info
        })
    else:
        return jsonify({
            'success': False,
            'message': f"Could not retrieve information for {ticker}"
        }), 404


@stock_api_bp.route('/stock/history/<ticker>', methods=['GET'])
@login_required
def api_stock_history(ticker):
    """
    Get historical price data for a stock.
    
    Args:
        ticker: Stock ticker symbol
    
    Query Params:
        period: Time period for historical data (default: '1mo')
        
    Returns:
        JSON response with historical price data or error message
    """
    ticker = ticker.upper()
    period = request.args.get('period', '1mo')
    
    # Validate period parameter
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    if period not in valid_periods:
        return jsonify({
            'success': False,
            'message': f"Invalid period parameter. Must be one of: {', '.join(valid_periods)}"
        }), 400
    
    historical_data = get_stock_historical_data(ticker, period)
    
    if historical_data:
        return jsonify({
            'success': True,
            'ticker': ticker,
            'period': period,
            'data': historical_data
        })
    else:
        return jsonify({
            'success': False,
            'message': f"Could not retrieve historical data for {ticker}"
        }), 404


@stock_api_bp.route('/stock/search', methods=['GET'])
@login_required
def api_stock_search():
    """
    Search for stocks by name or ticker.
    
    Query Params:
        q: Search query string
        
    Returns:
        JSON response with search results or error message
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({
            'success': False,
            'message': "Search query parameter 'q' is required"
        }), 400
    
    results = search_stocks(query)
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    })


@stock_api_bp.route('/market/summary', methods=['GET'])
@login_required
def api_market_summary():
    """
    Get summary of major market indices.
    
    Returns:
        JSON response with market summary data or error message
    """
    try:
        market_data = get_market_summary()
        
        return jsonify({
            'success': True,
            'data': market_data
        })
    except Exception as e:
        logger.error(f"Error in market summary API: {str(e)}")
        return jsonify({
            'success': False,
            'message': "Could not retrieve market summary"
        }), 500 