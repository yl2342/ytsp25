from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models.user import User

class RegistrationForm(FlaskForm):
    student_id = StringField('Yale Student ID', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_student_id(self, student_id):
        user = User.query.filter_by(student_id=student_id.data).first()
        if user:
            raise ValidationError('That student ID is already registered. Please use a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    student_id = StringField('Yale Student ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class FundDepositForm(FlaskForm):
    amount = FloatField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be positive')])
    submit = SubmitField('Deposit')


class FundWithdrawalForm(FlaskForm):
    amount = FloatField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be positive')])
    submit = SubmitField('Withdraw')


class StockSearchForm(FlaskForm):
    ticker = StringField('Stock Symbol / Ticker', validators=[DataRequired()])
    submit = SubmitField('Search')


class TradeForm(FlaskForm):
    ticker = HiddenField('Ticker', validators=[DataRequired()])
    company_name = HiddenField('Company Name', validators=[DataRequired()])
    action = SelectField('Action', choices=[('buy', 'Buy'), ('sell', 'Sell')], validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01, message='Quantity must be positive')])
    price = HiddenField('Current Price', validators=[DataRequired()])
    make_public = BooleanField('Share this trade with followers')
    trading_note = TextAreaField('Add a note about this trade (optional)', validators=[Length(max=500)])
    submit = SubmitField('Execute Trade')


class PostCommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post Comment')


class UserSearchForm(FlaskForm):
    student_id = StringField('Yale Student ID', validators=[DataRequired()])
    submit = SubmitField('Search')


class ReplyForm(FlaskForm):
    content = TextAreaField('Reply', validators=[DataRequired(), Length(max=500)])
    parent_id = HiddenField('Parent Comment ID', validators=[DataRequired()])
    submit = SubmitField('Post Reply') 