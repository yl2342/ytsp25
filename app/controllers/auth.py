"""
Authentication controllers for the Yale Trading Simulation Platform.
Handles user authentication and account management through Yale CAS integration.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_cas import login as cas_login, logout as cas_logout
from app import db, cas, login_manager
from app.models.user import User
from app.models.stock import CashTransaction
from app.forms import CasRegistrationForm, FundDepositForm, FundWithdrawalForm
from datetime import datetime
import zoneinfo

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle pre-CAS user registration.
    Collects user information before redirecting to CAS.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Get the NetID if user has already authenticated through CAS
    authenticated_netid = session.get('pending_netid', '')
    
    form = CasRegistrationForm()
    
    # Pre-fill the form with the NetID if available
    if request.method == 'GET' and authenticated_netid:
        form.net_id.data = authenticated_netid
    
    if form.validate_on_submit():
        # Create user with the registration data
        user = User(
            net_id=form.net_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            avatar_id=int(form.avatar_id.data)
        )
        db.session.add(user)
        db.session.commit()
        
        # Clear pending_netid from session since it's now registered
        if 'pending_netid' in session:
            session.pop('pending_netid')
            
        # If user has authenticated through CAS, log them in directly
        if 'CAS_USERNAME' in session and session['CAS_USERNAME'] == user.net_id:
            login_user(user)
            flash('Your account has been created! Welcome to the Yale Trading Simulation Platform.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Otherwise, store registration data in session and redirect to CAS
            flash('Registration successful! Please log in with Yale CAS.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form, authenticated_netid=authenticated_netid)

@auth_bp.route('/login')
def login():
    """Redirect to CAS login"""
    return cas_login()

@auth_bp.route('/logout')
def logout():
    """Log the user out and redirect to home page"""
    # First log out from Flask-Login
    logout_user()
    
    # Clear any CAS session data
    for key in list(session.keys()):
        if key.startswith('CAS_'):
            session.pop(key)
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))

# Let Flask-CAS handle the callback automatically
# We'll add this user initialization function that runs on each request
@auth_bp.before_app_request
def check_cas_login():
    """
    Check if user is authenticated through CAS and create/update user if needed.
    Runs on each request.
    """
    # First check if we have CAS data but no user
    if not current_user.is_authenticated and 'CAS_USERNAME' in session:
        net_id = session['CAS_USERNAME']
        
        # Check if user exists
        user = User.query.filter_by(net_id=net_id).first()
        
        # If the user doesn't exist, redirect to registration page
        if user is None:
            # Only redirect if not already on register page to avoid loops
            if request.endpoint != 'auth.register' and '/static/' not in request.path:
                # Store the NetID in session for pre-filling registration form
                session['pending_netid'] = net_id
                flash(f'No account found for NetID: {net_id}. Please complete registration to create an YTSP account first.', 'warning')
                return redirect(url_for('auth.register'))
            return None  # Continue with the request if already on register page
        
        # User exists, update the login timestamp and log them in
        user.last_login_edt = datetime.now(zoneinfo.ZoneInfo("America/New_York"))
        db.session.commit()
        
        # Log user in with Flask-Login
        login_user(user)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Display the user's profile information"""
    return render_template('auth/profile.html', title='My Profile')


@auth_bp.route('/funds/deposit', methods=['GET', 'POST'])
@login_required
def deposit_funds():
    """
    Handle fund deposits.
    GET: Display deposit form
    POST: Process deposit request and update account balance
    """
    form = FundDepositForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        if current_user.deposit(amount):
            # Create a cash transaction record
            cash_transaction = CashTransaction(
                user_id=current_user.id,
                transaction_type="deposit",
                amount=amount
            )
            db.session.add(cash_transaction)
            db.session.commit()
            flash(f'Successfully deposited ${amount:.2f} to your account.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid amount for deposit.', 'danger')
    
    return render_template('auth/deposit.html', title='Deposit Funds', form=form)


@auth_bp.route('/funds/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw_funds():
    """
    Handle fund withdrawals.
    GET: Display withdrawal form
    POST: Process withdrawal request and update account balance
    """
    form = FundWithdrawalForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        if current_user.withdraw(amount):
            # Create a cash transaction record
            cash_transaction = CashTransaction(
                user_id=current_user.id,
                transaction_type="withdraw",
                amount=amount
            )
            db.session.add(cash_transaction)
            db.session.commit()
            flash(f'Successfully withdrew ${amount:.2f} from your account.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid amount for withdrawal or insufficient funds.', 'danger')
    
    return render_template('auth/withdraw.html', title='Withdraw Funds', form=form)

@auth_bp.route('/clear-session')
def clear_session():
    """Clear all session data for troubleshooting or after database resets"""
    # Clear all session data
    session.clear()
    flash('All session data has been cleared. You can now register with your NetID again.', 'success')
    return redirect(url_for('main.home')) 