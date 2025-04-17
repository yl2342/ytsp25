from app import db
from app.models.stock import StockHolding, Transaction
from app.models.social import TradingPost
from app.utils.stock_utils import get_stock_info, get_current_price, get_stock_historical_data
from sqlalchemy.exc import SQLAlchemyError
import logging
import yfinance as yf

logger = logging.getLogger(__name__)

def execute_buy(user, ticker, quantity, price, make_public=False, trading_note=""):
    """
    Execute a buy order for a user
    
    Args:
        user: User model object
        ticker: Stock ticker symbol
        quantity: Number of shares to buy
        price: Current price per share
        make_public: Whether to make this trade public
        trading_note: Optional note about the trade
        
    Returns:
        tuple: (success: bool, message: str, transaction: Transaction or None)
    """
    try:
        # Log transaction details for debugging
        logger.info(f"Executing buy: {ticker}, quantity: {quantity}, price: {price}, user: {user.id}")
        
        # Verify user has enough balance
        total_cost = quantity * price
        if user.balance < total_cost:
            return False, "Insufficient funds for this purchase.", None
        
        # Deduct from user balance
        user.balance -= total_cost
        
        # Get stock info
        logger.info(f"Retrieving stock info for ticker: {ticker}")
        stock_info = get_stock_info(ticker)
        
        # If we couldn't get stock info but have a valid price, use basic info
        if not stock_info and price > 0:
            logger.warning(f"Could not retrieve full stock info for {ticker}, but continuing with basic info")
            stock_info = {
                'name': ticker,  # Use ticker as name if we don't have actual company name
                'ticker': ticker
            }
        
        if not stock_info:
            logger.error(f"Failed to retrieve stock information for {ticker}. Make sure the ticker symbol is valid.")
            return False, f"Could not retrieve stock information for {ticker}. Please try again with a valid ticker.", None
        
        # Log successful stock info retrieval
        logger.info(f"Stock info available for trade: {ticker} - {stock_info.get('name', 'Unknown')}")
        
        # Update or create stock holding
        holding = StockHolding.query.filter_by(user_id=user.id, ticker=ticker).first()
        
        if holding:
            # Update existing holding
            holding.update_holding(quantity, price)
        else:
            # Create new holding
            holding = StockHolding(
                user_id=user.id,
                ticker=ticker,
                company_name=stock_info.get('name', ticker),  # Use ticker as fallback
                quantity=quantity,
                buy_price=price
            )
            db.session.add(holding)
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            ticker=ticker,
            transaction_type="buy",
            quantity=quantity,
            price=price
        )
        db.session.add(transaction)
        
        # Create trading post if public
        if make_public:
            title = f"Bought {quantity} shares of {ticker}"
            content = trading_note if trading_note else f"I bought {quantity} shares of {ticker} at ${price:.2f} per share."
            post = TradingPost(
                user_id=user.id,
                title=title,
                content=content,
                ticker=ticker,
                trade_type="buy",
                quantity=quantity,
                price=price,
                is_public=True
            )
            db.session.add(post)
            
            # Link transaction to post
            transaction.trading_post_id = post.id
        
        db.session.commit()
        return True, f"Successfully purchased {quantity} shares of {ticker} at ${price:.2f} per share.", transaction
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during buy execution: {str(e)}")
        return False, "A database error occurred. Please try again.", None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error executing buy for {ticker}: {str(e)}")
        return False, "An error occurred while processing your purchase.", None


def execute_sell(user, ticker, quantity, price, make_public=False, trading_note=""):
    """
    Execute a sell order for a user
    
    Args:
        user: User model object
        ticker: Stock ticker symbol
        quantity: Number of shares to sell
        price: Current price per share
        make_public: Whether to make this trade public
        trading_note: Optional note about the trade
        
    Returns:
        tuple: (success: bool, message: str, transaction: Transaction or None)
    """
    try:
        # Log transaction details
        logger.info(f"Executing sell: {ticker}, quantity: {quantity}, price: {price}, user: {user.id}")
        
        # Check if user has the stock and enough shares
        holding = StockHolding.query.filter_by(user_id=user.id, ticker=ticker).first()
        
        if not holding or holding.quantity < quantity:
            return False, "You don't have enough shares to sell.", None
        
        # Calculate proceeds
        proceeds = quantity * price
        
        # Update holding
        success = holding.update_holding(-quantity, price)  # Negative quantity for selling
        if not success:
            return False, "Failed to update your stock holding.", None
        
        # Add to user balance
        user.balance += proceeds
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            ticker=ticker,
            transaction_type="sell",
            quantity=quantity,
            price=price
        )
        db.session.add(transaction)
        
        # Remove holding if quantity is zero
        if holding.quantity == 0:
            db.session.delete(holding)
        
        # Create trading post if public
        if make_public:
            title = f"Sold {quantity} shares of {ticker}"
            content = trading_note if trading_note else f"I sold {quantity} shares of {ticker} at ${price:.2f} per share."
            post = TradingPost(
                user_id=user.id,
                title=title,
                content=content,
                ticker=ticker,
                trade_type="sell",
                quantity=quantity,
                price=price,
                is_public=True
            )
            db.session.add(post)
            
            # Link transaction to post
            transaction.trading_post_id = post.id
        
        db.session.commit()
        return True, f"Successfully sold {quantity} shares of {ticker} at ${price:.2f} per share.", transaction
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during sell execution: {str(e)}")
        return False, "A database error occurred. Please try again.", None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error executing sell for {ticker}: {str(e)}")
        return False, "An error occurred while processing your sale.", None


def get_portfolio_summary(user):
    """
    Get a summary of the user's portfolio, including day change.
    
    Args:
        user: User model object
        
    Returns:
        dict: Portfolio summary information
    """
    try:
        holdings = StockHolding.query.filter_by(user_id=user.id).all()
        
        # Calculate portfolio statistics
        total_value = 0
        total_cost = 0
        total_day_change = 0
        stocks = []
        
        for holding in holdings:
            day_change = 0
            try:
                # Update current price
                current_price = get_current_price(holding.ticker)
                previous_close = 0

                # Fetch 2 days history to get previous close
                try:
                    stock_hist = yf.Ticker(holding.ticker).history(period="2d")
                    if not stock_hist.empty and len(stock_hist) >= 2:
                        previous_close = stock_hist['Close'].iloc[-2]
                    elif not stock_hist.empty:
                        # Fallback if only 1 day of data (e.g., new IPO)
                        previous_close = stock_hist['Close'].iloc[-1] 
                except Exception as hist_e:
                    logger.warning(f"Could not get history for {holding.ticker} to calculate day change: {hist_e}")

                # Protect against API failures for current price
                if current_price <= 0:
                    logger.warning(f"Got invalid current price (${current_price}) for {holding.ticker}, using last known price")
                    current_price = holding.current_price
                    if current_price <= 0:
                        logger.warning(f"Using average buy price for {holding.ticker} as current price fallback")
                        current_price = holding.average_buy_price
                
                # Only update the price in DB if we got a valid new price
                if current_price > 0:
                    holding.current_price = current_price
                
                # Calculate Day Change if we have previous close
                if previous_close > 0 and current_price > 0:
                    day_change = (current_price - previous_close) * holding.quantity
                    total_day_change += day_change
                
                # Calculate P/L values
                market_value = holding.quantity * holding.current_price
                cost_basis = holding.quantity * holding.average_buy_price
                profit_loss = market_value - cost_basis
                profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                # Add to totals
                total_value += market_value
                total_cost += cost_basis
                
                # Add stock details
                stocks.append({
                    'ticker': holding.ticker,
                    'company_name': holding.company_name,
                    'quantity': holding.quantity,
                    'average_price': holding.average_buy_price,
                    'current_price': holding.current_price,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'profit': profit_loss,
                    'profit_percent': profit_loss_percent,
                    'day_change': day_change
                })
            except Exception as stock_e:
                logger.error(f"Error processing holding {holding.ticker}: {str(stock_e)}")
                # Attempt to include stock with last known values even on error
                try:
                    market_value = holding.quantity * holding.current_price
                    cost_basis = holding.quantity * holding.average_buy_price
                    profit_loss = market_value - cost_basis
                    profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
                    day_change_fallback = 0

                    total_value += market_value
                    total_cost += cost_basis
                    # Don't add to total_day_change if error occurred

                    stocks.append({
                        'ticker': holding.ticker,
                        'company_name': holding.company_name,
                        'quantity': holding.quantity,
                        'average_price': holding.average_buy_price,
                        'current_price': holding.current_price,
                        'market_value': market_value,
                        'cost_basis': cost_basis,
                        'profit': profit_loss,
                        'profit_percent': profit_loss_percent,
                        'day_change': day_change_fallback
                    })
                except Exception as fallback_e:
                     logger.error(f"Failed to add fallback holding data for {holding.ticker}: {fallback_e}")

        
        # Calculate overall profit/loss
        total_profit_loss = total_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Commit price updates
        db.session.commit()
        
        return {
            'cash_balance': user.balance,
            'portfolio_value': total_value,
            'total_account_value': user.balance + total_value,
            'holdings': stocks,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percent': total_profit_loss_percent,
            'total_day_change': total_day_change
        }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error getting portfolio summary for user {user.id}: {str(e)}")
        # Return default structure on error
        return {
            'cash_balance': user.balance,
            'portfolio_value': 0,
            'total_account_value': user.balance,
            'holdings': [],
            'total_profit_loss': 0,
            'total_profit_loss_percent': 0,
            'total_day_change': 0 
        }


def ensure_public_transactions(user_id):
    """
    Ensures all transactions that should be public are correctly linked to public trading posts.
    
    This function finds any transactions that should be public but aren't correctly linked
    to a trading post, and fixes the relationship.
    
    Args:
        user_id: ID of the user whose transactions to check
        
    Returns:
        int: Number of transactions fixed
    """
    try:
        from app.models.social import TradingPost
        from app.models.stock import Transaction
        
        # Get all transactions without a trading_post_id
        unlinked_transactions = Transaction.query.filter_by(
            user_id=user_id,
            trading_post_id=None
        ).all()
        
        if not unlinked_transactions:
            return 0
            
        fixed_count = 0
        
        for transaction in unlinked_transactions:
            # Check if a trading post exists for this transaction
            # but isn't linked (can happen if the transaction was created first)
            existing_post = TradingPost.query.filter_by(
                user_id=user_id,
                ticker=transaction.ticker,
                trade_type=transaction.transaction_type,
                quantity=transaction.quantity,
                price=transaction.price
            ).first()
            
            if existing_post and existing_post.is_public:
                # Link the transaction to the existing post
                transaction.trading_post_id = existing_post.id
                fixed_count += 1
                logger.info(f"Linked transaction {transaction.id} to existing trading post {existing_post.id}")
            
        if fixed_count > 0:
            db.session.commit()
            logger.info(f"Fixed {fixed_count} public transactions for user {user_id}")
            
        return fixed_count
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error fixing public transactions for user {user_id}: {str(e)}")
        return 0


def create_missing_public_posts(user_id):
    """
    Creates public trading posts for any transaction without one, 
    assuming the user wanted to share them publicly.
    
    Call this function with caution as it will make all transactions public.
    Best used as an admin function or one-time fix.
    
    Args:
        user_id: ID of the user whose transactions to check
        
    Returns:
        int: Number of public posts created
    """
    try:
        from app.models.social import TradingPost
        from app.models.stock import Transaction
        from app.models.user import User
        
        # Get user info for better post content
        user = User.query.get(user_id)
        if not user:
            return 0
            
        # Get all transactions without a trading_post_id
        unlinked_transactions = Transaction.query.filter_by(
            user_id=user_id,
            trading_post_id=None
        ).all()
        
        if not unlinked_transactions:
            return 0
            
        created_count = 0
        
        for transaction in unlinked_transactions:
            # Create a new public trading post for this transaction
            trade_type = transaction.transaction_type
            title = f"{'Bought' if trade_type == 'buy' else 'Sold'} {transaction.quantity} shares of {transaction.ticker}"
            content = f"I {'bought' if trade_type == 'buy' else 'sold'} {transaction.quantity} shares of {transaction.ticker} at ${transaction.price:.2f} per share."
            
            post = TradingPost(
                user_id=user_id,
                title=title,
                content=content,
                ticker=transaction.ticker,
                trade_type=trade_type,
                quantity=transaction.quantity,
                price=transaction.price,
                is_public=True
            )
            db.session.add(post)
            db.session.flush()  # Get post ID
            
            # Link the transaction to the post
            transaction.trading_post_id = post.id
            created_count += 1
            
        if created_count > 0:
            db.session.commit()
            logger.info(f"Created {created_count} public posts for user {user_id}")
            
        return created_count
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating public posts for user {user_id}: {str(e)}")
        return 0 