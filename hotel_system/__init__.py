import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'hotel_reservation'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///HotelDB.db'

ROOT = os.path.dirname(os.path.abspath(__file__))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# adds functionality to database models
login_manager = LoginManager(app)
# checks that a user is curently logged in
login_manager.login_view = 'employee_login'
login_manager.login_message = 'You have to log in to access this page.'


from hotel_system import routes
