from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.forms import StockSearchForm, TradeForm
from app.utils.stock_utils import get_stock_info, get_stock_historical_data, search_stocks, get_popular_stocks
from app.utils.trading_utils import execute_buy, execute_sell, get_portfolio_summary
from app.models.stock import StockHolding, Transaction
import logging

trading_bp = Blueprint('trading', __name__)

logger = logging.getLogger(__name__)

@trading_bp.route('/search', methods=['GET', 'POST'])
@login_required
def stock_search():
    try:
        form = StockSearchForm()
        results = []
        searched = False
        
        if form.validate_on_submit() or request.args.get('ticker'):
            ticker = form.ticker.data or request.args.get('ticker')
            ticker = ticker.upper().strip()
            searched = True
            
            logger.info(f"Searching for stock with ticker/query: '{ticker}'")
            
            # First try direct lookup by ticker
            stock_info = get_stock_info(ticker)
            if stock_info:
                logger.info(f"Direct ticker lookup successful for '{ticker}'")
                results = [stock_info]
            else:
                # If direct lookup fails, try search
                logger.info(f"Direct ticker lookup failed for '{ticker}', trying search")
                results = search_stocks(ticker)
                
            logger.info(f"Found {len(results)} results for search '{ticker}'")
            
            if not results:
                flash(f"No stocks found matching '{ticker}'. Try another search term or ticker symbol.", "warning")
        
        # Get popular stocks for the sidebar
        popular_stocks = get_popular_stocks()
                
        return render_template('trading/search.html', 
                            title='Stock Search',
                            form=form,
                            results=results,
                            searched=searched,
                            popular_stocks=popular_stocks)
    except Exception as e:
        logger.error(f"Error in stock_search: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash("An error occurred while searching for stocks. Please try again.", "danger")
        return render_template('trading/search.html', 
                            title='Stock Search',
                            form=form,
                            results=[],
                            searched=False,
                            popular_stocks=[])


@trading_bp.route('/stock/<ticker>')
@login_required
def stock_detail(ticker):
    try:
        ticker = ticker.upper()
        logger.info(f"Accessing stock detail for ticker: {ticker}")
        
        stock_info = get_stock_info(ticker)
        
        if not stock_info:
            logger.warning(f"No stock information found for ticker: {ticker}")
            flash(f"Could not find information for ticker: {ticker}", "danger")
            return redirect(url_for('trading.stock_search'))
        
        logger.info(f"Successfully retrieved stock info for {ticker}: {stock_info['name']}")
        
        # Get historical data for charts
        historical_data = get_stock_historical_data(ticker, period='6mo')
        
        # Check if user owns this stock
        user_holding = StockHolding.query.filter_by(user_id=current_user.id, ticker=ticker).first()
        
        # Create trade form
        trade_form = TradeForm()
        trade_form.ticker.data = ticker
        trade_form.company_name.data = stock_info['name']
        trade_form.price.data = stock_info['current_price']
        
        # Get user's recent transactions for this stock
        recent_transactions = Transaction.query.filter_by(
            user_id=current_user.id, 
            ticker=ticker
        ).order_by(
            Transaction.timestamp.desc()
        ).limit(5).all()
        
        return render_template('trading/stock_detail.html',
                            title=f"{ticker} - {stock_info['name']}",
                            stock=stock_info,
                            historical_data=historical_data,
                            user_holding=user_holding,
                            trade_form=trade_form,
                            recent_transactions=recent_transactions)
    except Exception as e:
        logger.error(f"Error in stock_detail for ticker {ticker}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash(f"An error occurred while retrieving stock information. Please try again.", "danger")
        return redirect(url_for('trading.stock_search'))


@trading_bp.route('/trade', methods=['POST'])
@login_required
def execute_trade():
    form = TradeForm()
    
    if form.validate_on_submit():
        ticker = form.ticker.data.upper()
        company_name = form.company_name.data
        action = form.action.data
        quantity = form.quantity.data
        price = float(form.price.data)
        make_public = form.make_public.data
        trading_note = form.trading_note.data
        
        if action == 'buy':
            success, message, transaction = execute_buy(
                current_user, ticker, quantity, price, make_public, trading_note
            )
        else:  # action == 'sell'
            success, message, transaction = execute_sell(
                current_user, ticker, quantity, price, make_public, trading_note
            )
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
            
        return redirect(url_for('trading.stock_detail', ticker=ticker))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")
    
    return redirect(url_for('trading.stock_search'))


@trading_bp.route('/portfolio')
@login_required
def portfolio():
    # Get portfolio summary
    portfolio_summary = get_portfolio_summary(current_user)
    
    # Get transaction history
    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Transaction.timestamp.desc()
    ).all()
    
    return render_template('trading/portfolio.html',
                           title='My Portfolio',
                           portfolio=portfolio_summary,
                           transactions=transactions)


@trading_bp.route('/api/stock/price/<ticker>')
@login_required
def get_current_stock_price(ticker):
    """API endpoint to get the current price of a stock"""
    ticker = ticker.upper()
    stock_info = get_stock_info(ticker)
    
    if stock_info:
        return jsonify({
            'success': True,
            'ticker': ticker,
            'price': stock_info['current_price']
        })
    else:
        return jsonify({
            'success': False,
            'message': f"Could not retrieve information for {ticker}"
        }), 404 