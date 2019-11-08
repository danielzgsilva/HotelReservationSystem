from hotel_system.forms import RegistrationForm, LoginForm
from hotel_system.models import Employee
from flask import Flask, render_template, send_from_directory, request, session, flash, url_for, redirect
from hotel_system import app, db, bcrypt
from hotel_system.reservation import Reservation
from hotel_system.utils import get_int_date, get_availability

import os
import secrets

@app.route("/")
def index():
    return render_template('index.html', title='Home', single_count = -1, double_count = -1, deluxe_count = -1)

@app.route('/', methods=['GET', 'POST'])
def check_availability():
    # Get user input
    num_guests = int(request.form.get('guest_num_input'))
    check_in = str(request.form.get('check_in'))
    check_out = str(request.form.get('check_out'))

    date_in = get_int_date(check_in)
    date_out = get_int_date(check_out)

    # Querying hotel database
    single_count, double_count, deluxe_count = get_availability(num_guests, date_in, date_out)

    return render_template('index.html', title='Home', num_guests = num_guests, check_in = check_in, check_out = check_out,
                           single_count = single_count, double_count = double_count, deluxe_count = deluxe_count, scroll = 'bottom')

@app.route('/booking', methods=['GET'])
def make_reservation():
    # Get user input
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    room_type = request.args.get('room')

    # Instantiate reservation class
    new_reservation = Reservation(check_in, check_out, room_type)

    # Store reservation in flask session in order for other routes to access it's variables
    session['new_reservation'] = new_reservation.__dict__

    return render_template('make_reservation.html', title='Booking', reservation=new_reservation)

@app.route('/booking', methods=['GET', 'POST'])
def store_reservation():
    # Rebuild reservation class from session variables
    reservation_vars = session['new_reservation']
    reservation = Reservation(reservation_vars['check_in'], reservation_vars['check_out'], reservation_vars['room_type'])

    # Get user input
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    wifi = request.form.get('wifi')
    tv = request.form.get('tv')
    parking = request.form.get('parking')
    pool = request.form.get('pool')

    # Store reservation data in hotel database
    reservation.store_reservation(first_name, last_name, email, phone, wifi, tv, parking, pool)

    message = "We've booked your stay for {} nights! We look forward towards seeing you!".format(reservation.length)
    return render_template('success.html', title='Success', message = message)

@app.route('/employee_portal', methods=['GET'])
def employee_portal():
    return render_template('employee_portal.html', title='Employee Portal')

# employee login route
@app.route('/employee_login', methods=['GET','POST'])
def employee_login():
    #if current_user.is_authenticated:
        #return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # checking user is in database
        #employee = Employee.query.filter_by(email=form.email.data).first()
        #if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            #login_user(user, remember=form.remember.data)
            # get's the page that user tried to enter that
            # redirected then to log in
            #next_page = request.args.get('next')
            #return redirect(next_page) if next_page else redirect(url_for('home'))
        #else:
            #flash('Login Unsuccessful. Please check email and password', 'danger')
        flash('You have been logged in!')
        return redirect(url_for('employee_portal'))
    return render_template('employee_login.html', title = "Login", form = form)

@app.route('/employee_registration', methods=['GET','POST'])
def employee_registration():
    # redirects user if they're already logged in
    #if current_user.is_authenticated:
        #return redirect(url_for('home'))

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
        flash(f'Your account has been create! You are now able to log in','success')
        return redirect(url_for('employee_login'))
    return render_template('employee_registration.html', title="Register", form=form)

@app.route('/<filename>')
def load_image(filename):
    return send_from_directory('static/', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500

