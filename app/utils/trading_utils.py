from app import db
from app.models.stock import StockHolding, Transaction
from app.models.social import TradingPost
from app.utils.stock_utils import get_stock_info, get_current_price
from sqlalchemy.exc import SQLAlchemyError
import logging

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
        # Verify user has enough balance
        total_cost = quantity * price
        if user.balance < total_cost:
            return False, "Insufficient funds for this purchase.", None
        
        # Deduct from user balance
        user.balance -= total_cost
        
        # Get stock info
        stock_info = get_stock_info(ticker)
        if not stock_info:
            return False, "Could not retrieve stock information.", None
        
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
                company_name=stock_info['name'],
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
        if make_public and trading_note:
            title = f"Bought {quantity} shares of {ticker}"
            post = TradingPost(
                user_id=user.id,
                title=title,
                content=trading_note,
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
        if make_public and trading_note:
            title = f"Sold {quantity} shares of {ticker}"
            post = TradingPost(
                user_id=user.id,
                title=title,
                content=trading_note,
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
    Get a summary of the user's portfolio
    
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
        stocks = []
        
        for holding in holdings:
            # Update current price
            current_price = get_current_price(holding.ticker)
            if current_price > 0:
                holding.current_price = current_price
            
            # Calculate values
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
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent
            })
        
        # Calculate overall profit/loss
        total_profit_loss = total_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Commit price updates
        db.session.commit()
        
        return {
            'cash_balance': user.balance,
            'portfolio_value': total_value,
            'total_account_value': user.balance + total_value,
            'stocks': stocks,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percent': total_profit_loss_percent
        }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error getting portfolio summary for user {user.id}: {str(e)}")
        return {
            'cash_balance': user.balance,
            'portfolio_value': 0,
            'total_account_value': user.balance,
            'stocks': [],
            'total_profit_loss': 0,
            'total_profit_loss_percent': 0
        } 