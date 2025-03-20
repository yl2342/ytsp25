from datetime import datetime,timezone
import zoneinfo
from app import db
from sqlalchemy.sql import func

class StockHolding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    average_buy_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, ticker, company_name, quantity, buy_price):
        self.user_id = user_id
        self.ticker = ticker
        self.company_name = company_name
        self.quantity = quantity
        self.average_buy_price = buy_price
        self.current_price = buy_price  # Initialize with buy price, will be updated regularly

    def update_holding(self, quantity_change, price):
        """Update stock holding after a buy/sell transaction"""
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
        self.last_updated = datetime.utcnow()
        return True

    def get_market_value(self):
        """Get the current market value of this holding"""
        return self.quantity * self.current_price

    def get_profit_loss(self):
        """Calculate profit/loss for this holding"""
        return self.quantity * (self.current_price - self.average_buy_price)

    def get_profit_loss_percentage(self):
        """Calculate profit/loss percentage"""
        if self.average_buy_price == 0:
            return 0
        return ((self.current_price - self.average_buy_price) / self.average_buy_price) * 100

    def __repr__(self):
        return f"StockHolding('{self.ticker}', {self.quantity} shares)"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default= datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    trading_post_id = db.Column(db.Integer, db.ForeignKey('trading_post.id'), nullable=True)

    def __init__(self, user_id, ticker, transaction_type, quantity, price):
        self.user_id = user_id
        self.ticker = ticker
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price = price
        self.total_amount = quantity * price

    def __repr__(self):
        return f"Transaction('{self.ticker}', '{self.transaction_type}', {self.quantity} @ ${self.price:.2f})"


class CashTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'deposit' or 'withdraw'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))

    def __init__(self, user_id, transaction_type, amount):
        self.user_id = user_id
        self.transaction_type = transaction_type
        self.amount = amount

    def __repr__(self):
        return f"CashTransaction('{self.transaction_type}', ${self.amount:.2f})" 