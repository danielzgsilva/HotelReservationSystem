from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
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
    credit_card = StringField('Credit Card Number', validators = [DataRequired(), Length(min=16, max=20, message='Invalid Card Number')])
    expiry_month = StringField('Expiration Month', validators=[DataRequired(), Length(min=2, max=2, message='Invalid Month')])
    expiry_year = StringField('Expiration Year', validators=[DataRequired(), Length(min=4, max=4, message='Invalid Year')])
    card_ccv = StringField('CCV', validators=[DataRequired(), Length(min=3, max=3, message='Invalid CCV')])
    card_name = StringField('Name on the Card', validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField('Place Reservation')

# form for creating a work order
class WorkOrderForm(FlaskForm):
    room_num = IntegerField('Room Number', validators=[DataRequired()])
    type = StringField('Type (20 Character Limit)', validators=[DataRequired(), Length(max=20)])
    comments = TextAreaField('Comments (120 Character Limit)', validators=[Length(max=120)])
    submit = SubmitField('Place Work Order')

    def validate_room_num(self, room_num):
        valid = 1 <= room_num.data <= 30
        if not valid:
            raise ValidationError('Room number is not valid. Please input a valid room number.')