from datetime import datetime, timezone
import zoneinfo
from flask_login import UserMixin
from app import db, login_manager, bcrypt
from sqlalchemy.sql import func

# Followers association table for the many-to-many relationship
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    net_id = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at_edt = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    last_login_edt = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    is_active = db.Column(db.Boolean, default=True)
    
    # Portfolio holdings
    portfolio = db.relationship('StockHolding', backref='user', lazy=True)
    
    # Transactions history
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    # Trading posts
    posts = db.relationship('TradingPost', backref='author', lazy=True)
    
    # Comments made by user
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    # Follows relationship
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )
    
    def __init__(self, net_id, password, first_name, last_name):
        self.net_id = net_id
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def deposit(self, amount):
        if amount <= 0:
            return False
        self.balance += amount
        return True
    
    def withdraw(self, amount):
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True
    
    def follow(self, user):
        if not self.is_following(user) and self != user:
            self.followed.append(user)
            return True
        return False
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return True
        return False
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        from app.models.trading_post import TradingPost
        return TradingPost.query.join(
            followers, (followers.c.followed_id == TradingPost.user_id)
        ).filter(
            followers.c.follower_id == self.id,
            TradingPost.is_public == True
        ).order_by(
            TradingPost.created_at.desc()
        )
    
    def get_portfolio_value(self):
        total_value = 0.0
        for holding in self.portfolio:
            # This would need to fetch current stock prices
            total_value += holding.quantity * holding.current_price
        return total_value
    
    def __repr__(self):
        return f"User('{self.net_id}')"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 