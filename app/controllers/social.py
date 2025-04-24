from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.user import User, followers as followers_table
from app.models.social import TradingPost, Comment, PostInteraction
from app.forms import UserSearchForm, PostCommentForm, ReplyForm
from app.utils.stock_utils import get_trending_stocks, get_popular_stocks
from app.models.stock import Transaction
from app.models.stock import StockHolding
from app.utils.trading_utils import ensure_public_transactions, create_missing_public_posts
import logging

logger = logging.getLogger(__name__)

social_bp = Blueprint('social', __name__)

@social_bp.route('/search-users', methods=['GET', 'POST'])
@login_required
def search_users():
    form = UserSearchForm()
    results = []
    searched = False
    
    # Get sort parameter (default to 'followers')
    sort_by = request.args.get('sort_by', 'followers')
    
    # Check if this is a partial request
    is_partial = request.args.get('partial', '0') == '1'
    
    if form.validate_on_submit() or request.args.get('net_id'):
        # Get search term from form or URL parameters - keeping 'net_id' param name for compatibility
        search_term = form.net_id.data or request.args.get('net_id')
        searched = True
        
        users = User.query.filter(User.net_id.contains(search_term)).all()
        
        # Exclude current user from results
        results = [user for user in users if user.id != current_user.id]
    
    # Get popular users based on selected sorting
    if sort_by == 'transactions':
        # Sort by transaction count - need to join with Transaction table to count
        from sqlalchemy import func
        
        # Create a subquery to get transaction counts
        transaction_counts = db.session.query(
            Transaction.user_id, 
            func.count(Transaction.id).label('tx_count')
        ).group_by(Transaction.user_id).subquery()
        
        # Join with User table and order by transaction count
        popular_users = User.query.join(
            transaction_counts,
            User.id == transaction_counts.c.user_id
        ).order_by(
            transaction_counts.c.tx_count.desc()
        ).limit(5).all()
        
        # Attach transaction counts to user objects for display
        for user in popular_users:
            user.tx_count = db.session.query(func.count(Transaction.id)).filter(
                Transaction.user_id == user.id
            ).scalar() or 0
    else:
        # Default: Sort by follower count
        popular_users = User.query.join(
            followers_table,
            (followers_table.c.followed_id == User.id)
        ).group_by(User.id).order_by(
            db.func.count(followers_table.c.follower_id).desc()
        ).limit(5).all()
    
    # If this is a partial request, only return the Popular Yale Traders section
    if is_partial:
        return render_template('social/partials/popular_users.html',
                               popular_users=popular_users,
                               sort_by=sort_by)
    
    return render_template('social/search_users.html',
                           title='Find Yale Traders',
                           form=form,
                           results=results,
                           searched=searched,
                           popular_users=popular_users,
                           sort_by=sort_by)


@social_bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    # Fix any public transactions that aren't properly linked
    ensure_public_transactions(user_id)
    
    # Get public trading posts by this user
    posts = TradingPost.query.filter_by(
        user_id=user_id, 
        is_public=True
    ).order_by(
        TradingPost.created_at.desc()
    ).all()
    
    # Get user's public stock transactions
    public_transactions = Transaction.query.join(
        TradingPost, 
        Transaction.trading_post_id == TradingPost.id
    ).filter(
        Transaction.user_id == user_id,
        TradingPost.is_public == True
    ).order_by(
        Transaction.timestamp.desc()
    ).all()
    
    # Get top holdings if this is the current user or if the current user is following this user
    top_holdings = []
    is_following = current_user.is_following(user)
    if user.id == current_user.id or is_following:
        holdings = StockHolding.query.filter_by(user_id=user_id).order_by(StockHolding.current_price * StockHolding.quantity.desc()).limit(5).all()
        total_value = sum(holding.get_market_value() for holding in holdings)
        for holding in holdings:
            if total_value > 0:
                percentage = (holding.get_market_value() / total_value) * 100
            else:
                percentage = 0
            top_holdings.append({
                'ticker': holding.ticker,
                'quantity': holding.quantity,
                'percentage': percentage
            })
    
    return render_template('social/user_profile.html',
                           title=f"{user.first_name} {user.last_name}'s Profile",
                           user=user,
                           posts=posts,
                           is_following=is_following,
                           public_transactions=public_transactions,
                           holdings=top_holdings)


@social_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot follow yourself.", "warning")
    else:
        if current_user.follow(user):
            db.session.commit()
            flash(f"You are now following {user.first_name} {user.last_name}.", "success")
        else:
            flash(f"You are already following {user.first_name} {user.last_name}.", "info")
    
    return redirect(url_for('social.user_profile', user_id=user_id))


@social_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if current_user.unfollow(user):
        db.session.commit()
        flash(f"You have unfollowed {user.first_name} {user.last_name}.", "success")
    else:
        flash(f"You are not following {user.first_name} {user.last_name}.", "info")
    
    return redirect(url_for('social.user_profile', user_id=user_id))


@social_bp.route('/following')
@social_bp.route('/following/<int:user_id>')
@login_required
def following(user_id=None):
    """Show users that the current user is following"""
    if user_id is None:
        user = current_user
        title = 'People I Follow'
    else:
        user = User.query.get_or_404(user_id)
        title = f"People {user.first_name} Follows"
    
    followed_users = user.followed.all()
    
    return render_template('social/following.html',
                           title=title,
                           followed_users=followed_users,
                           profile_user=user)


@social_bp.route('/followers')
@social_bp.route('/followers/<int:user_id>')
@login_required
def followers(user_id=None):
    """Show users who follow the current user"""
    if user_id is None:
        user = current_user
        title = 'My Followers'
    else:
        user = User.query.get_or_404(user_id)
        title = f"{user.first_name}'s Followers"
    
    follower_users = User.query.join(
        followers_table, 
        (followers_table.c.follower_id == User.id)
    ).filter(
        followers_table.c.followed_id == user.id
    ).all()
    
    return render_template('social/followers.html',
                           title=title,
                           followers=follower_users,
                           profile_user=user)


@social_bp.route('/feed')
@login_required
def feed():
    """Show social feed of posts from followed users"""
    try:
        # Get posts from followed users
        followed_posts = current_user.followed_posts().all()
        
        # Get global popular posts (that aren't already in followed posts)
        followed_user_ids = [user.id for user in current_user.followed.all()]
        followed_user_ids.append(current_user.id)  # Add current user ID
        
        # Create subqueries for likes and dislikes counts
        likes_count = db.session.query(
            PostInteraction.post_id,
            db.func.count(PostInteraction.id).label('likes_count')
        ).filter(
            PostInteraction.interaction_type == 'like'
        ).group_by(
            PostInteraction.post_id
        ).subquery()
        
        dislikes_count = db.session.query(
            PostInteraction.post_id,
            db.func.count(PostInteraction.id).label('dislikes_count')
        ).filter(
            PostInteraction.interaction_type == 'dislike'
        ).group_by(
            PostInteraction.post_id
        ).subquery()
        
        # Get popular posts (most liked, most recent)
        popular_posts = TradingPost.query.outerjoin(
            likes_count,
            TradingPost.id == likes_count.c.post_id
        ).outerjoin(
            dislikes_count,
            TradingPost.id == dislikes_count.c.post_id
        ).filter(
            TradingPost.user_id.notin_(followed_user_ids),
            TradingPost.is_public == True
        ).order_by(
            db.func.coalesce(likes_count.c.likes_count, 0).desc(),
            TradingPost.created_at.desc()
        ).limit(10).all()
        
        # Get trending stocks for the sidebar
        trending_stocks = get_trending_stocks()
        
        return render_template('social/feed.html',
                            title='Social Feed',
                            followed_posts=followed_posts,
                            popular_posts=popular_posts,
                            trending_stocks=trending_stocks)
    except Exception as e:
        logger.error(f"Error loading social feed for user {current_user.id}: {str(e)}")
        flash("An error occurred while loading your feed. Please try again.", "danger")
        return render_template('social/feed.html',
                            title='Social Feed',
                            followed_posts=[],
                            popular_posts=[],
                            trending_stocks=[])


@social_bp.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    """View a single trading post with comments"""
    post = TradingPost.query.get_or_404(post_id)
    
    # Check if post is public or belongs to current user
    if not post.is_public and post.user_id != current_user.id:
        flash("You don't have permission to view this post.", "danger")
        return redirect(url_for('social.feed'))
    
    # Get root-level comments
    comments = Comment.query.filter_by(
        post_id=post_id,
        parent_id=None
    ).order_by(
        Comment.created_at.desc()
    ).all()
    
    # Forms for comments
    comment_form = PostCommentForm()
    reply_form = ReplyForm()
    
    return render_template('social/post_detail.html',
                           title='Trading Post',
                           post=post,
                           comments=comments,
                           comment_form=comment_form,
                           reply_form=reply_form)


@social_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a trading post"""
    post = TradingPost.query.get_or_404(post_id)
    form = PostCommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            post_id=post_id,
            user_id=current_user.id,
            content=form.content.data
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been added.", "success")
    
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_to_comment(comment_id):
    """Reply to a comment"""
    parent_comment = Comment.query.get_or_404(comment_id)
    form = ReplyForm()
    
    if form.validate_on_submit():
        reply = Comment(
            post_id=parent_comment.post_id,
            user_id=current_user.id,
            content=form.content.data,
            parent_id=comment_id
        )
        db.session.add(reply)
        db.session.commit()
        flash("Your reply has been added.", "success")
    
    return redirect(url_for('social.view_post', post_id=parent_comment.post_id))


@social_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Toggle like on a trading post"""
    post = TradingPost.query.get_or_404(post_id)
    
    # Check if user already liked this post
    existing_like = PostInteraction.query.filter_by(
        user_id=current_user.id,
        post_id=post_id,
        interaction_type='like'
    ).first()
    
    liked = False
    if existing_like:
        # User already liked the post, remove the like
        db.session.delete(existing_like)
    else:
        # User hasn't liked the post, add a like
        # First remove any existing dislike
        existing_dislike = PostInteraction.query.filter_by(
            user_id=current_user.id,
            post_id=post_id,
            interaction_type='dislike'
        ).first()
        if existing_dislike:
            db.session.delete(existing_dislike)
        
        # Add the like
        like = PostInteraction(
            user_id=current_user.id,
            post_id=post_id,
            interaction_type='like'
        )
        db.session.add(like)
        liked = True
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        button_class = "btn-primary" if liked else "btn-outline-primary"
        return f'''
            <button class="btn btn-sm {button_class} me-2" 
                   hx-post="{url_for('social.like_post', post_id=post.id)}"
                   hx-swap="outerHTML"
                   hx-target="this"
                   hx-headers='{{"X-Requested-With": "XMLHttpRequest"}}'>
                <i class="far fa-thumbs-up me-1"></i> 
                <span id="post-likes-{post.id}">{post.likes}</span>
            </button>
        '''
    
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/post/<int:post_id>/dislike', methods=['POST'])
@login_required
def dislike_post(post_id):
    """Toggle dislike on a trading post"""
    post = TradingPost.query.get_or_404(post_id)
    
    # Check if user already disliked this post
    existing_dislike = PostInteraction.query.filter_by(
        user_id=current_user.id,
        post_id=post_id,
        interaction_type='dislike'
    ).first()
    
    disliked = False
    if existing_dislike:
        # User already disliked the post, remove the dislike
        db.session.delete(existing_dislike)
    else:
        # User hasn't disliked the post, add a dislike
        # First remove any existing like
        existing_like = PostInteraction.query.filter_by(
            user_id=current_user.id,
            post_id=post_id,
            interaction_type='like'
        ).first()
        if existing_like:
            db.session.delete(existing_like)
        
        # Add the dislike
        dislike = PostInteraction(
            user_id=current_user.id,
            post_id=post_id,
            interaction_type='dislike'
        )
        db.session.add(dislike)
        disliked = True
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        button_class = "btn-secondary" if disliked else "btn-outline-secondary"
        return f'''
            <button class="btn btn-sm {button_class}" 
                   hx-post="{url_for('social.dislike_post', post_id=post.id)}"
                   hx-swap="outerHTML"
                   hx-target="this"
                   hx-headers='{{"X-Requested-With": "XMLHttpRequest"}}'>
                <i class="far fa-thumbs-down me-1"></i> 
                <span id="post-dislikes-{post.id}">{post.dislikes}</span>
            </button>
        '''
    
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/my-posts')
@login_required
def my_posts():
    """View all posts made by the current user"""
    posts = TradingPost.query.filter_by(
        user_id=current_user.id
    ).order_by(
        TradingPost.created_at.desc()
    ).all()
    
    return render_template('social/my_posts.html',
                           title='My Trading Posts',
                           posts=posts)


@social_bp.route('/post/<int:post_id>/toggle-visibility', methods=['POST'])
@login_required
def toggle_post_visibility(post_id):
    """Toggle a post between public and private"""
    post = TradingPost.query.get_or_404(post_id)
    
    # Check if post belongs to current user
    if post.user_id != current_user.id:
        flash("You don't have permission to modify this post.", "danger")
        return redirect(url_for('social.feed'))
    
    # Toggle visibility
    is_public = post.toggle_visibility()
    db.session.commit()
    
    status = "public" if is_public else "private"
    flash(f"Post is now {status}.", "success")
    
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/make_all_public')
@login_required
def make_all_transactions_public():
    """A utility route to make all of the current user's transactions public"""
    try:
        count = create_missing_public_posts(current_user.id)
        if count > 0:
            flash(f"Successfully made {count} of your transactions public.", "success")
        else:
            flash("No transactions needed to be made public.", "info")
    except Exception as e:
        logger.error(f"Error making transactions public: {str(e)}")
        flash("An error occurred while trying to make your transactions public.", "danger")
        
    return redirect(url_for('social.user_profile', user_id=current_user.id)) 