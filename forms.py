from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import sqlite3 as sql

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

    def validate_email(self, email_field):
        email = email_field.data
        conn = sql.connect('database/HotelDB.db')
        cur = conn.cursor()

        # Create query which will search the reservations table for open rooms
        query = "SELECT Username FROM Employees WHERE Username=?"
        cur.execute(query, (email,))
        num_emails = cur.fetchall()

        conn.close()
        if len(num_emails) > 0:
            raise ValidationError('This email is already present. Please try again')

    def validate_admin_flag(self, admin_flag):
        key = admin_flag.data
        if str(key) not in ['Admin', 'Standard']:
            raise ValidationError('Invalid key. Please try again.')





