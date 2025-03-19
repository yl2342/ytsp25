from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models.user import User
from app.forms import RegistrationForm, LoginForm, FundDepositForm, FundWithdrawalForm
from datetime import datetime
import zoneinfo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            net_id=form.net_id.data,
            password=form.password.data,  # This will be hashed in the __init__ method
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(net_id=form.net_id.data).first()
        
        if user and user.check_password(form.password.data):
            # Update the last login timestamp
            user.last_login_edt = datetime.now(zoneinfo.ZoneInfo("America/New_York"))
            db.session.commit()
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your Net ID and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('auth/profile.html', title='My Profile')


@auth_bp.route('/funds/deposit', methods=['GET', 'POST'])
@login_required
def deposit_funds():
    form = FundDepositForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        if current_user.deposit(amount):
            db.session.commit()
            flash(f'Successfully deposited ${amount:.2f} to your account.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid amount for deposit.', 'danger')
    
    return render_template('auth/deposit.html', title='Deposit Funds', form=form)


@auth_bp.route('/funds/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw_funds():
    form = FundWithdrawalForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        if current_user.withdraw(amount):
            db.session.commit()
            flash(f'Successfully withdrew ${amount:.2f} from your account.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid amount for withdrawal or insufficient funds.', 'danger')
    
    return render_template('auth/withdraw.html', title='Withdraw Funds', form=form) 