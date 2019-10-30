from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


# Form for user Login
class LoginForm(FlaskForm):
    email = StringField('Email', validators =[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Login')

# Form for user registration
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators =[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    admin_flag = IntegerField('Company Role Assign', validators = [DataRequired()])
    submit = SubmitField('Sign Up')
