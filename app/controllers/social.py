from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.user import User
from app.models.social import TradingPost, Comment
from app.forms import UserSearchForm, PostCommentForm, ReplyForm
from app.utils.stock_utils import get_trending_stocks, get_popular_stocks
import logging

logger = logging.getLogger(__name__)

social_bp = Blueprint('social', __name__)

@social_bp.route('/search-users', methods=['GET', 'POST'])
@login_required
def search_users():
    form = UserSearchForm()
    results = []
    searched = False
    
    if form.validate_on_submit() or request.args.get('student_id'):
        # Get search term from form or URL parameters - keeping 'student_id' param name for compatibility
        search_term = form.student_id.data or request.args.get('student_id')
        searched = True
        
        # Search for users by net_id instead of student_id
        users = User.query.filter(User.net_id.contains(search_term)).all()
        
        # Exclude current user from results
        results = [user for user in users if user.id != current_user.id]
    
    return render_template('social/search_users.html',
                           title='Find Yale Traders',
                           form=form,
                           results=results,
                           searched=searched)


@social_bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get public trading posts by this user
    posts = TradingPost.query.filter_by(
        user_id=user_id, 
        is_public=True
    ).order_by(
        TradingPost.created_at.desc()
    ).all()
    
    # Check if current user is following this user
    is_following = current_user.is_following(user)
    
    return render_template('social/user_profile.html',
                           title=f"{user.first_name} {user.last_name}'s Profile",
                           user=user,
                           posts=posts,
                           is_following=is_following)


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
@login_required
def following():
    """Show users that the current user is following"""
    followed_users = current_user.followed.all()
    
    return render_template('social/following.html',
                           title='People I Follow',
                           followed_users=followed_users)


@social_bp.route('/followers')
@login_required
def followers():
    """Show users who follow the current user"""
    followers = User.query.join(
        User.followed,
        (User.followed.any(id=current_user.id))
    ).all()
    
    return render_template('social/followers.html',
                           title='My Followers',
                           followers=followers)


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
        
        # Get popular posts (most liked, most recent)
        popular_posts = TradingPost.query.filter(
            TradingPost.user_id.notin_(followed_user_ids),
            TradingPost.is_public == True
        ).order_by(
            TradingPost.likes.desc(),
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
    """Like a trading post"""
    post = TradingPost.query.get_or_404(post_id)
    post.like()
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'likes': post.likes})
    
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/post/<int:post_id>/dislike', methods=['POST'])
@login_required
def dislike_post(post_id):
    """Dislike a trading post"""
    post = TradingPost.query.get_or_404(post_id)
    post.dislike()
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'dislikes': post.dislikes})
    
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