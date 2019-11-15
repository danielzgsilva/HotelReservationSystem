from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import sqlite3 as sql
from hotel_system.models import Employee

# Form for user Login
class LoginForm(FlaskForm):
    email = StringField('Email', validators =[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Login')

# Form for user registration
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators =[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    admin_flag = StringField('Company Role Assign', validators = [DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = Employee.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Email is taken, please use another one.')


    def validate_admin_flag(self, admin_flag):
        key = admin_flag.data
        if str(key) not in ['Admin', 'Standard']:
            raise ValidationError('Invalid key. Please try again.')

# form for reservation
class ReservationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators =[DataRequired(), Email()])
    phone = StringField('Phone Number', validators = [DataRequired(), Length(min=10, max=12)])
    credit_card = StringField('Credit Card Number', validators = [DataRequired(), Length(min=19, max=20)])
    submit = SubmitField('Place Reservation')
