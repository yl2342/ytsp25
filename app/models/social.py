"""
Social interaction models for the Yale Trading Simulation Platform.
Defines the database models for social features like trading posts and comments.
"""
from datetime import datetime, timezone
import zoneinfo
from app import db
from sqlalchemy.sql import func

class PostInteraction(db.Model):
    """
    Tracks user interactions (likes/dislikes) with posts.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('trading_post.id'), nullable=False)
    interaction_type = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    
    # Relationships
    user = db.relationship('User', backref='post_interactions')
    post = db.relationship('TradingPost', backref='interactions')
    
    # Unique constraint to prevent multiple interactions of the same type
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', 'interaction_type', name='unique_user_post_interaction'),
    )

    def __init__(self, user_id, post_id, interaction_type):
        """
        Initialize a new post interaction.
        
        Args:
            user_id: The ID of the user
            post_id: The ID of the post
            interaction_type: Either 'like' or 'dislike'
        """
        self.user_id = user_id
        self.post_id = post_id
        self.interaction_type = interaction_type

    def __repr__(self):
        """String representation of PostInteraction object"""
        return f"PostInteraction(User ID: {self.user_id}, Post ID: {self.post_id}, Type: {self.interaction_type})"

class TradingPost(db.Model):
    """
    Represents a user's post about a trade they made.
    Can be public or private and can receive likes, dislikes and comments.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    transaction = db.relationship('Transaction', backref='post', uselist=False)

    def __init__(self, user_id, title, content, ticker, trade_type, quantity, price, is_public=True):
        """
        Initialize a new trading post.
        
        Args:
            user_id: The ID of the post author
            title: Post title
            content: Post content/body
            ticker: The stock ticker symbol
            trade_type: Either 'buy' or 'sell'
            quantity: Number of shares traded
            price: Price per share at time of trade
            is_public: Whether the post is visible to others (default True)
        """
        self.user_id = user_id
        self.title = title
        self.content = content
        self.ticker = ticker
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.is_public = is_public

    @property
    def likes(self):
        """Get the number of likes for this post"""
        return PostInteraction.query.filter_by(
            post_id=self.id,
            interaction_type='like'
        ).count()
        
    @property
    def dislikes(self):
        """Get the number of dislikes for this post"""
        return PostInteraction.query.filter_by(
            post_id=self.id,
            interaction_type='dislike'
        ).count()
        
    def toggle_visibility(self):
        """
        Toggle whether the post is public or private.
        
        Returns:
            The new visibility state
        """
        self.is_public = not self.is_public
        return self.is_public

    def __repr__(self):
        """String representation of TradingPost object"""
        return f"TradingPost('{self.title}', '{self.ticker}', '{self.trade_type}')"


class Comment(db.Model):
    """
    Represents a comment on a trading post.
    Can be a direct comment or a reply to another comment.
    """
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('trading_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    
    # Relationship for nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def __init__(self, post_id, user_id, content, parent_id=None):
        """
        Initialize a new comment.
        
        Args:
            post_id: The ID of the post being commented on
            user_id: The ID of the comment author
            content: The comment text
            parent_id: The ID of the parent comment if this is a reply (default None)
        """
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.parent_id = parent_id

    def __repr__(self):
        """String representation of Comment object"""
        return f"Comment(Post ID: {self.post_id}, User ID: {self.user_id}, Reply: {self.parent_id is not None})" 