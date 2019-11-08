import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = 'hotel_reservation'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///HotelDB.db'

ROOT = os.path.dirname(os.path.abspath(__file__))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


from hotel_system import routes