"""
Forms for the Yale Trading Simulation Platform.
Defines all WTForms classes used for user input throughout the application.
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, 
    TextAreaField, FloatField, SelectField, HiddenField, RadioField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
)
from app.models.user import User

class CasRegistrationForm(FlaskForm):
    """Form for new user registration with CAS"""
    net_id = StringField('Yale Net ID', validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    avatar_id = RadioField('Choose Your Avatar', choices=[(str(i), f'Avatar {i}') for i in range(1, 10)], 
                          validators=[DataRequired()], default='1')
    submit = SubmitField('Proceed to Yale Login')

    def validate_net_id(self, net_id):
        """Validates that the NetID is not already in use"""
        user = User.query.filter_by(net_id=net_id.data).first()
        if user:
            raise ValidationError('That Net ID is already registered. Please login instead.')

class FundDepositForm(FlaskForm):
    """Form for adding funds to account"""
    amount = FloatField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be positive')])
    submit = SubmitField('Deposit')


class FundWithdrawalForm(FlaskForm):
    """Form for withdrawing funds from account"""
    amount = FloatField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be positive')])
    submit = SubmitField('Withdraw')


class StockSearchForm(FlaskForm):
    """Form for searching stocks by ticker symbol"""
    ticker = StringField('Stock Symbol / Ticker', validators=[DataRequired()])
    submit = SubmitField('Search')


class TradeForm(FlaskForm):
    """Form for executing stock trades (buy/sell)"""
    ticker = HiddenField('Ticker', validators=[DataRequired()])
    company_name = HiddenField('Company Name', validators=[DataRequired()])
    action = SelectField('Action', choices=[('buy', 'Buy'), ('sell', 'Sell')], validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01, message='Quantity must be positive')])
    price = HiddenField('Current Price', validators=[DataRequired()])
    make_public = BooleanField('Share this trade with followers')
    trading_note = TextAreaField('Add a note about this trade (optional)', validators=[Length(max=500)])
    submit = SubmitField('Execute Trade')


class PostCommentForm(FlaskForm):
    """Form for adding comments to trading posts"""
    content = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post Comment')


class UserSearchForm(FlaskForm):
    """Form for searching users by NetID"""
    net_id = StringField('Yale Net ID', validators=[DataRequired()])
    submit = SubmitField('Search')


class ReplyForm(FlaskForm):
    """Form for replying to comments"""
    content = TextAreaField('Reply', validators=[DataRequired(), Length(max=500)])
    parent_id = HiddenField('Parent Comment ID', validators=[DataRequired()])
    submit = SubmitField('Post Reply') 