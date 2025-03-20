from datetime import datetime, timezone
import zoneinfo
from app import db
from sqlalchemy.sql import func

class TradingPost(db.Model):
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
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    transaction = db.relationship('Transaction', backref='post', uselist=False)

    def __init__(self, user_id, title, content, ticker, trade_type, quantity, price, is_public=True):
        self.user_id = user_id
        self.title = title
        self.content = content
        self.ticker = ticker
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.is_public = is_public

    def like(self):
        self.likes += 1
        
    def dislike(self):
        self.dislikes += 1
        
    def toggle_visibility(self):
        self.is_public = not self.is_public
        return self.is_public

    def __repr__(self):
        return f"TradingPost('{self.title}', '{self.ticker}', '{self.trade_type}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('trading_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(zoneinfo.ZoneInfo("America/New_York")))
    
    # Replies to this comment
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def __init__(self, post_id, user_id, content, parent_id=None):
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.parent_id = parent_id

    def __repr__(self):
        return f"Comment(Post ID: {self.post_id}, User ID: {self.user_id}, Reply: {self.parent_id is not None})" 