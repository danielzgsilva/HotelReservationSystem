from datetime import datetime
from hotel_system import db

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable = False)
    last_name = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    admin_flag = db.Column(db.Boolean, nullable = False)

    def __repr__(self):
        return f"Employee('{self.email}', '{self.password}', '{self.admin_flag}')"

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(10), nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    credit_card = db.Column(db.String(19), nullable = False)
    check_in = db.Column(db.Integer, nullable=False)
    check_out = db.Column(db.Integer, nullable=False)
    tv = db.Column(db.Boolean, nullable = False)
    wifi = db.Column(db.Boolean, nullable = False)
    pool = db.Column(db.Boolean, nullable = False)
    room_type = db.Column(db.String(6), nullable = False)
    room_num = db.Column(db.Integer)

    def __repr__(self):
        return f"Reservation('{self.email}', '{self.check_in}', '{self.check_out}', '{self.tv}', '{self.wifi}', '{self.pool}', '{self.room_type}', '{self.room_num}')"

class WorkOrder(db.Model):
    order_number = db.Column(db.Integer, nullable = False, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    room_num = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)

    def __repr__(self):
        return f"WorkOrder('{self.type}', '{self.room_num}', '{self.employee_id}')"

class Room(db.Model):
    room_num = db.Column(db.Integer, nullable = False, primary_key=True)
    room_type = db.Column(db.String(6), nullable=False)
    capacity = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Room('{self.room_num}', '{self.room_type}', '{self.capacity}')"


