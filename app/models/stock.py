"""
Stock related models for the Yale Trading Simulation Platform.
Defines the database models for stock holdings, transactions, and cash movements.
"""
from datetime import datetime, timezone
import zoneinfo
from app import db
from sqlalchemy.sql import func

class StockHolding(db.Model):
    """
    Represents a user's holding of a particular stock.
    Tracks quantity, purchase price, and current price.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    average_buy_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")), 
                            onupdate=datetime.now(zoneinfo.ZoneInfo("America/New_York")))

    def __init__(self, user_id, ticker, company_name, quantity, buy_price):
        """
        Initialize a new stock holding.
        
        Args:
            user_id: The ID of the user who owns this holding
            ticker: The stock ticker symbol
            company_name: The name of the company
            quantity: Number of shares
            buy_price: Purchase price per share
        """
        self.user_id = user_id
        self.ticker = ticker
        self.company_name = company_name
        self.quantity = quantity
        self.average_buy_price = buy_price
        self.current_price = buy_price  # Initialize with buy price, will be updated regularly

    def update_holding(self, quantity_change, price):
        """
        Update stock holding after a buy/sell transaction.
        
        Args:
            quantity_change: Change in number of shares (positive for buy, negative for sell)
            price: Current price per share
            
        Returns:
            Boolean indicating success of the operation
        """
        if self.quantity + quantity_change < 0:
            return False  # Not enough shares to sell
        
        if quantity_change > 0:  # Buying more shares
            # Update average price
            total_value = (self.quantity * self.average_buy_price) + (quantity_change * price)
            self.quantity += quantity_change
            self.average_buy_price = total_value / self.quantity
        else:  # Selling shares
            self.quantity += quantity_change  # quantity_change is negative for sells
        
        self.current_price = price
        self.last_updated = datetime.now(zoneinfo.ZoneInfo("America/New_York"))
        return True

    def get_market_value(self):
        """
        Calculate the current market value of this holding.
        
        Returns:
            Float value of current holdings
        """
        return self.quantity * self.current_price

    def get_profit_loss(self):
        """
        Calculate profit/loss for this holding.
        
        Returns:
            Float representing total profit or loss
        """
        return self.quantity * (self.current_price - self.average_buy_price)

    def get_profit_loss_percentage(self):
        """
        Calculate profit/loss as a percentage.
        
        Returns:
            Float percentage of profit/loss
        """
        if self.average_buy_price == 0:
            return 0
        return ((self.current_price - self.average_buy_price) / self.average_buy_price) * 100

    def __repr__(self):
        """String representation of StockHolding object"""
        return f"StockHolding('{self.ticker}', {self.quantity} shares)"


class Transaction(db.Model):
    """
    Represents a stock transaction (buy or sell).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    trading_post_id = db.Column(db.Integer, db.ForeignKey('trading_post.id'), nullable=True)

    def __init__(self, user_id, ticker, transaction_type, quantity, price):
        """
        Initialize a new transaction.
        
        Args:
            user_id: The ID of the user making the transaction
            ticker: The stock ticker symbol
            transaction_type: Either 'buy' or 'sell'
            quantity: Number of shares
            price: Price per share
        """
        self.user_id = user_id
        self.ticker = ticker
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price = price
        self.total_amount = quantity * price

    def __repr__(self):
        """String representation of Transaction object"""
        return f"Transaction('{self.ticker}', '{self.transaction_type}', {self.quantity} @ ${self.price:.2f})"


class CashTransaction(db.Model):
    """
    Represents a cash deposit or withdrawal.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'deposit' or 'withdraw'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))

    def __init__(self, user_id, transaction_type, amount):
        """
        Initialize a new cash transaction.
        
        Args:
            user_id: The ID of the user making the transaction
            transaction_type: Either 'deposit' or 'withdraw'
            amount: The cash amount
        """
        self.user_id = user_id
        self.transaction_type = transaction_type
        self.amount = amount

    def __repr__(self):
        """String representation of CashTransaction object"""
        return f"CashTransaction('{self.transaction_type}', ${self.amount:.2f})" 