from hotel_system.forms import RegistrationForm, LoginForm, ReservationForm, WorkOrderForm
from hotel_system.models import Employee, Reservation, WorkOrder
from flask import Flask, render_template, send_from_directory, request, session, flash, url_for, redirect
from hotel_system import app, db, bcrypt
from hotel_system.utils import get_int_date, get_availability, temp_reservation
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required

import random
import os
import secrets

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html', title='Home', single_count = -1, double_count = -1, deluxe_count = -1)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def check_availability():
    # Get user input
    num_guests = int(request.form.get('guest_num_input'))
    check_in = str(request.form.get('check_in'))
    check_out = str(request.form.get('check_out'))

    date_in = get_int_date(check_in)
    date_out = get_int_date(check_out)
    today = int(str(datetime.today().year) + str(datetime.today().month) + str(datetime.today().day))

    if date_out - date_in <= 0 or date_in < today:
        message = 'The dates are not valid!  '+str(today)+'  '+ str(date_in)+ '  ' + str(date_out)
        return render_template('failure.html', title='Home', message=message)

    # Querying hotel database
    single_count, double_count, deluxe_count, avail_rooms = get_availability(num_guests, date_in, date_out)

    session['available'] = avail_rooms

    return render_template('index.html', title='Home', num_guests = num_guests, check_in = check_in, check_out = check_out,
                           single_count = single_count, double_count = double_count, deluxe_count = deluxe_count, scroll = 'bottom')

@app.route('/booking', methods=['GET'])
def make_reservation():
    form = ReservationForm()

    # Get user input
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    room_type = request.args.get('room')

    # Filter available rooms based on guest selection
    session['available'] = [i for i in session['available'] if i[1] == room_type]

    # Instantiate reservation class
    new_reservation = temp_reservation(check_in, check_out, room_type)

    # Store reservation in flask session in order for other routes to access it's variables
    session['new_reservation'] = new_reservation.__dict__

    return render_template('make_reservation.html', title='Booking', reservation=new_reservation, form=form)

@app.route('/booking_success', methods=['GET', 'POST'])
def store_reservation():
    # Rebuild reservation class from session variables
    temp = session['new_reservation']
    reservation = temp_reservation(temp['check_in'], temp['check_out'], temp['room_type'])

    form = ReservationForm()

    if form.validate_on_submit():
        # Get user input
        wifi = False if request.form.get('wifi') is None else True
        tv = False if request.form.get('tv') is None else True
        parking = False if request.form.get('parking') is None else True
        pool = False if request.form.get('pool') is None else True

        # Assign the reservation a room number
        room_nums = [int(i[0]) for i in session['available']]
        room_num = min(room_nums)

        reservation = Reservation(first_name=form.first_name.data, last_name=form.last_name.data,
         email=form.email.data, phone=form.phone.data,
         credit_card=form.credit_card.data, check_in=get_int_date(temp['check_in']),
         check_out=get_int_date(temp['check_out']), tv=tv, wifi=wifi, pool=pool,
         room_type=temp['room_type'], room_num=room_num)

        db.session.add(reservation)
        db.session.commit()
        flash(f'Your reservation has been created!','success')
        return redirect(url_for('index'))
    else:
        flash(f'Error! Please check your fields below.','danger')
        return render_template('make_reservation.html', title="Booking", reservation=reservation, form=form)

@app.route('/employee_portal', methods=['GET'])
@login_required
def employee_portal():
    return render_template('employee_portal.html', title='Employee Portal')

# employee login route
@app.route('/employee_login', methods=['GET','POST'])
def employee_login():
    if current_user.is_authenticated:
        return redirect(url_for('employee_portal'))
    form = LoginForm()
    if form.validate_on_submit():
        # checking user is in database
        employee = Employee.query.filter_by(email=form.email.data).first()
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            login_user(employee)
            flash('You have been logged in!', 'success')
            return redirect(url_for('employee_portal'))
            # get's the page that user tried to enter that
            # redirected then to log in
            #next_page = request.args.get('next')
            #return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
    return render_template('employee_login.html', title = "Login", form = form)

@app.route('/employee_registration', methods=['GET','POST'])
def employee_registration():
    # redirects user if they're already logged in
    if current_user.is_authenticated:
        return redirect(url_for('employee_portal'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # hashing password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # create admin_flag
        if form.admin_flag.data == 'Admin':
            flag = True
        else:
            flag = False

        # create employee
        # add employee to database
        employee = Employee(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password, admin_flag=flag)
        db.session.add(employee)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in','success')
        return redirect(url_for('employee_login'))
    return render_template('employee_registration.html', title="Register", form=form)

@app.route('/employee_logout')
def employee_logout():
    logout_user()
    return redirect(url_for('employee_login'))

@app.route('/create_work_order', methods=['GET','POST'])
@login_required
def create_work_order():
    form = WorkOrderForm()
    if form.validate_on_submit():
        standard_employees = Employee.query.filter_by(admin_flag=0).all()
        employee_id = random.choice(standard_employees).id
        work_order = WorkOrder(type=form.type.data, room_num=form.room_num.data, employee_id=employee_id, comments=form.comments.data)
        db.session.add(work_order)
        db.session.commit()
        flash(f'The work order has been assigned!', 'success')
        return redirect(url_for('create_work_order'))
    return render_template('create_work_order.html', title="create_work_order", form=form)


@app.route('/<filename>')
def load_image(filename):
    return send_from_directory('static/', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500
