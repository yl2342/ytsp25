"""
API endpoints for user data in the Yale Trading Simulation Platform.
Provides routes for retrieving user information, transactions, and portfolio data.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.stock import Transaction
from app.utils.trading_utils import get_portfolio_summary
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint for user API endpoints
user_api_bp = Blueprint('user_api', __name__)

@user_api_bp.route('/transactions/recent', methods=['GET'])
@login_required
def get_recent_transactions():
    """
    Get the user's most recent transactions.
    
    Returns:
        JSON response with the user's recent transactions (max 100)
    """
    try:
        limit = 100  # Maximum number of transactions to return
        
        transactions = Transaction.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Transaction.timestamp.desc()
        ).limit(limit).all()
        
        # Convert transactions to JSON-serializable format
        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                'id': transaction.id,
                'ticker': transaction.ticker,
                'transaction_type': transaction.transaction_type,
                'quantity': transaction.quantity,
                'price': transaction.price,
                'total_amount': transaction.total_amount,
                'timestamp': transaction.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'transactions': transactions_list
        })
        
    except Exception as e:
        logger.error(f"Error fetching recent transactions: {str(e)}")
        return jsonify({
            'success': False,
            'message': "An error occurred while fetching your transactions."
        }), 500 

@user_api_bp.route('/portfolio/summary', methods=['GET'])
@login_required
def get_portfolio_data():
    """
    Get the user's portfolio summary data.
    
    Returns:
        JSON response with the user's portfolio summary
    """
    try:
        portfolio_summary = get_portfolio_summary(current_user)
        
        return jsonify({
            'success': True,
            'portfolio': portfolio_summary
        })
        
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {str(e)}")
        return jsonify({
            'success': False,
            'message': "An error occurred while fetching your portfolio data."
        }), 500 