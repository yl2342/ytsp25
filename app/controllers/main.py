from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.utils.stock_utils import get_market_summary, get_trending_stocks, get_popular_stocks
from app.utils.trading_utils import get_portfolio_summary
from app.models.social import TradingPost
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Landing page for the application"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Get market summary for the landing page
    try:
        market_indices = get_market_summary()
    except Exception as e:
        logger.error(f"Error getting market summary for homepage: {str(e)}")
        market_indices = []
    
    return render_template('main/home.html', 
                           title='Yale Trading Simulation',
                           market_indices=market_indices)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for logged-in users"""
    try:
        # Get portfolio summary
        portfolio = get_portfolio_summary(current_user)
        
        # Get market summary
        market_indices = get_market_summary()
        
        # Get trending and popular stocks
        trending_stocks = get_trending_stocks()
        popular_stocks = get_popular_stocks()
        
        # Get recent activity from people the user follows
        followed_posts = current_user.followed_posts().limit(10).all()
        
        # Get user's recent stock transactions
        from app.models.stock import Transaction, CashTransaction
        from sqlalchemy import desc, union_all
        
        # Get stock transactions
        stock_transactions = Transaction.query.filter_by(user_id=current_user.id)\
                                         .order_by(Transaction.timestamp.desc())
        
        # Get cash transactions
        cash_transactions = CashTransaction.query.filter_by(user_id=current_user.id)\
                                         .order_by(CashTransaction.timestamp.desc())
        
        # Combine both types of transactions, sort by timestamp, and limit to 5
        all_transactions = []
        for tx in stock_transactions.limit(10).all():
            all_transactions.append({
                'type': 'stock',
                'transaction': tx,
                'timestamp': tx.timestamp
            })
        
        for tx in cash_transactions.limit(10).all():
            all_transactions.append({
                'type': 'cash',
                'transaction': tx,
                'timestamp': tx.timestamp
            })
        
        # Sort combined transactions by timestamp (most recent first)
        recent_transactions = sorted(
            all_transactions, 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:5]
        
        # Get global activity feed (public posts)
        global_posts = TradingPost.query.filter_by(is_public=True)\
                                   .order_by(TradingPost.created_at.desc())\
                                   .limit(5)\
                                   .all()
                               
    except Exception as e:
        logger.error(f"Error loading dashboard for user {current_user.id}: {str(e)}")
        portfolio = {
            'cash_balance': current_user.balance,
            'portfolio_value': 0,
            'total_account_value': current_user.balance,
            'stocks': [],
            'total_profit_loss': 0,
            'total_profit_loss_percent': 0
        }
        market_indices = []
        trending_stocks = []
        popular_stocks = []
        followed_posts = []
        recent_transactions = []
        global_posts = []
    
    return render_template('main/dashboard.html',
                           title='Dashboard',
                           portfolio=portfolio,
                           market_indices=market_indices,
                           trending_stocks=trending_stocks,
                           popular_stocks=popular_stocks,
                           followed_posts=followed_posts,
                           recent_transactions=recent_transactions,
                           global_posts=global_posts)


@main_bp.route('/about')
def about():
    """About page with information about the platform"""
    return render_template('main/about.html', title='About Yale Trading')


@main_bp.route('/help')
def help():
    """Help and documentation page"""
    return render_template('main/help.html', title='Help & Documentation') 