"""
User model and related functionality for the Yale Trading Simulation Platform.
Handles user authentication, profile management, and relationships between users.
"""
from datetime import datetime, timezone
import zoneinfo
import random
from flask_login import UserMixin
from app import db, login_manager, bcrypt
from sqlalchemy.sql import func

# Association table for the many-to-many followers relationship
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    """
    User model representing a platform user and their attributes.
    Inherits from UserMixin to provide Flask-Login functionality.
    """
    # Basic user information
    id = db.Column(db.Integer, primary_key=True)
    net_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    balance = db.Column(db.Float, default=1000.0)
    avatar_id = db.Column(db.Integer, default=0) # 0 for default, 1-9 for other avatars
    created_at_edt = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    last_login_edt = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    portfolio = db.relationship('StockHolding', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    cash_transactions = db.relationship('CashTransaction', backref='user', lazy=True)
    posts = db.relationship('TradingPost', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    # Follows relationship
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )
    
    def __init__(self, net_id, first_name=None, last_name=None, avatar_id=None):
        """
        Initialize a new user with the provided information.
        
        Args:
            net_id: The Yale NetID (username)
            first_name: User's first name (optional)
            last_name: User's last name (optional)
            avatar_id: User's avatar ID (optional, randomly assigned if not provided)
        """
        self.net_id = net_id
        self.first_name = first_name
        self.last_name = last_name
        # Use provided avatar_id or randomly assign one
        self.avatar_id = avatar_id if avatar_id is not None else random.randint(1, 9)

    def deposit(self, amount):
        """
        Add funds to the user's account.
        
        Args:
            amount: The amount to deposit
            
        Returns:
            Boolean indicating success
        """
        if amount <= 0:
            return False
        self.balance += amount
        return True
    
    def withdraw(self, amount):
        """
        Withdraw funds from the user's account.
        
        Args:
            amount: The amount to withdraw
            
        Returns:
            Boolean indicating success
        """
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True
    
    def follow(self, user):
        """
        Follow another user.
        
        Args:
            user: The User object to follow
            
        Returns:
            Boolean indicating success
        """
        if not self.is_following(user) and self != user:
            self.followed.append(user)
            return True
        return False
    
    def unfollow(self, user):
        """
        Unfollow a user.
        
        Args:
            user: The User object to unfollow
            
        Returns:
            Boolean indicating success
        """
        if self.is_following(user):
            self.followed.remove(user)
            return True
        return False
    
    def is_following(self, user):
        """
        Check if this user is following another user.
        
        Args:
            user: The User object to check
            
        Returns:
            Boolean indicating if following
        """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        """
        Get trading posts from followed users.
        
        Returns:
            Query for posts by followed users, newest first
        """
        from app.models.social import TradingPost
        return TradingPost.query.join(
            followers, (followers.c.followed_id == TradingPost.user_id)
        ).filter(
            followers.c.follower_id == self.id,
            TradingPost.is_public == True
        ).order_by(
            TradingPost.created_at.desc()
        )
    
    def get_portfolio_value(self):
        """
        Calculate the current total value of user's portfolio.
        
        Returns:
            Float representing the portfolio value
        """
        total_value = 0.0
        for holding in self.portfolio:
            total_value += holding.quantity * holding.current_price
        return total_value
    
    def get_avatar_url(self):
        """
        Get the URL for the user's avatar.
        
        Returns:
            String representing the avatar URL path
        """
        if self.avatar_id == 0:
            return 'img/avatars/default.png'
        return f'img/avatars/avatar{self.avatar_id}.png'
    
    def __repr__(self):
        """String representation of User object"""
        return f"User('{self.net_id}')"


@login_manager.user_loader
def load_user(user_id):
    """
    User loader for Flask-Login.
    
    Args:
        user_id: The user ID to load
        
    Returns:
        User object or None if not found
    """
    return User.query.get(int(user_id)) 