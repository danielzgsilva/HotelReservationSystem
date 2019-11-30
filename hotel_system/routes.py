from hotel_system.forms import *
from hotel_system.models import *
from flask import Flask, render_template, send_from_directory, request, session, flash, url_for, redirect
from hotel_system import app, db, bcrypt
from hotel_system.utils import *
from datetime import datetime, date
from flask_login import login_user, current_user, logout_user, login_required
import bisect

import random
import os
import secrets

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html', title='Home', room_counts = {'single': -1, 'double': -1, 'deluxe': -1})

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def check_availability():
    # Get user input
    num_guests = int(request.form.get('guest_num_input'))
    check_in = str(request.form.get('check_in'))
    check_out = str(request.form.get('check_out'))

    date_in = get_int_date(check_in)
    date_out = get_int_date(check_out)
    today = get_int_date(str(date.today()))

    if date_out - date_in <= 0 or date_in < today:
        flash(f'These dates are not valid!', 'danger')
        return render_template('index.html', title='Home', room_counts = {'single': -1, 'double': -1, 'deluxe': -1})

    # Querying hotel database
    room_counts, avail_rooms, room_buckets = get_availability(num_guests, date_in, date_out)

    session['available'] = avail_rooms

    return render_template('index.html', title='Home', num_guests = num_guests, check_in = check_in, check_out = check_out,
                           room_counts = room_counts, scroll = 'bottom')

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
    print(current_user.admin_flag)
    return render_template('employee_portal.html', title='Employee Portal', admin_flag=current_user.admin_flag)

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
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
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
        comment = str(date.today()) + ' - ' + form.comments.data
        work_order = WorkOrder(type=form.type.data, room_num=form.room_num.data, employee_id=employee_id, comments=comment)
        db.session.add(work_order)
        db.session.commit()
        flash(f'The work order has been assigned!', 'success')
        return redirect(url_for('create_work_order'))
    return render_template('create_work_order.html', title="Create Work Order", form=form)


@app.route('/create_service_order', methods=['GET','POST'])
@login_required
def create_service_order():
    form = RoomServiceForm()
    if form.validate_on_submit():
        standard_employees = Employee.query.filter_by(admin_flag=0).all()
        employee_id = random.choice(standard_employees).id

        # Create services list and calculate price
        services_list = []
        price = 0.00
        if form.toiletries.data:
            price = price + 2.00
            services_list.append('toiletries')
        if form.food.data:
            price = price + 5.00
            services_list.append('food')
        if form.bedding.data:
            price = price + 3.00
            services_list.append('bedding')
        if form.other.data:
            price = price + 6.00
            services_list.append('other')

        services_string = ",".join(services_list)
        service_order = RoomService(room_num=form.room_num.data, employee_id=employee_id, price=price, services=services_string, comments=form.comments.data)
        db.session.add(service_order)
        db.session.commit()
        flash(f'The service order has been assigned!', 'success')
        return redirect(url_for('create_service_order'))
    return render_template('create_service_order.html', title="Create Service Order", form=form)

@app.route('/receipt', methods=['GET','POST'])
@login_required
def print_receipt():
    form = PrintReceiptForm()
    if form.validate_on_submit():
        reservation_data = Reservation.query.filter_by(email = form.email.data, room_num = form.room_num.data).all()[-1]
        room_service_data = RoomService.query.filter_by(room_num = form.room_num.data).all()

        if reservation_data is None:
            flash(f'Information not found! Please try again.', 'danger')

        cost_per_night = prices[reservation_data.room_type]
        reservation_data.date_created = str(reservation_data.date_created).split()[0]
        reservation_data.room_type = str(reservation_data.room_type).capitalize()
        length_of_stay = (datetime.strptime(str(reservation_data.check_out), '%Y%m%d') - datetime.strptime(str(reservation_data.check_in), '%Y%m%d')).days

        if room_service_data is not None:
            room_services = {'toiletries': 0, 'food': 0, 'bedding': 0, 'other': 0}
            # Loop through each individual order
            for order in room_service_data:
                # Loop through items on an order
                for item in order.services.split(','):
                    room_services[item.lower()] += 1

        flash(f'You may print the receipt below!', 'success')
        return render_template('receipt.html', title='Receipt', reservation = reservation_data, length = length_of_stay, cost_pn = cost_per_night, room_service = room_services)
    return render_template('print_receipt.html', title="Print Receipt", form=form)

@app.route('/view_reservations', methods=['GET', 'POST'])
@login_required
def view_reservations():
    if not check_for_admin(current_user.admin_flag):
        flash(f'You must be an admin to access this page!','danger')
        return redirect(url_for('employee_portal'))
    form = ViewReservationsForm()
    # Get all reservations
    reservations = Reservation.query.all()

    if form.validate_on_submit():
        new_reservations = []
        # filter reservations based on inputted parameters
        for res in reservations:
            if form.first_name.data.strip().lower() == "" or str(res.first_name).strip().lower() == form.first_name.data.strip().lower():
                if form.last_name.data.strip().lower() == "" or str(res.last_name).strip().lower() == form.last_name.data.strip().lower():
                    if form.email.data.strip().lower() == "" or str(res.email).strip().lower() == form.email.data.strip().lower():
                        if form.room_type.data.strip().lower() == "" or str(res.room_type).strip().lower() == form.room_type.data.strip().lower():
                            if form.check_in.data is None or res.check_in >= form.check_in.data:
                                if form.check_out.data is None or res.check_out <= form.check_out.data:
                                    new_reservations.append(res)

        return render_template('view_reservations.html', title="Reservations", form=form, reservations = new_reservations)
    return render_template('view_reservations.html', title="Reservations", form=form, reservations = reservations)


@app.route('/view_guests', methods=['GET', 'POST'])
@login_required
def view_guests():
    if not check_for_admin(current_user.admin_flag):
        flash(f'You must be an admin to access this page!','danger')
        return redirect(url_for('employee_portal'))
    form = ViewGuestsForm()
    # Get all reservations
    guests = Reservation.query.all()

    if form.validate_on_submit():
        new_guests = []
        # filter reservations based on inputted parameters
        for guest in guests:
            if form.first_name.data.strip().lower() == "" or str(guest.first_name).strip().lower() == form.first_name.data.strip().lower():
                if form.last_name.data.strip().lower() == "" or str(guest.last_name).strip().lower() == form.last_name.data.strip().lower():
                    if form.email.data.strip().lower() == "" or str(guest.email).strip().lower() == form.email.data.strip().lower():
                        if form.phone.data.strip().lower() == "" or str(guest.phone).strip().lower() == form.phone.data.strip().lower():
                            if form.credit_card.data.strip().lower() == "" or str(guest.credit_card).strip().lower() == form.credit_card.data.strip().lower():
                                if form.room_num.data is None or guest.room_num == form.room_num.data:
                                    new_guests.append(guest)

        return render_template('view_guests.html', title="Guests", form=form, guests=new_guests)
    return render_template('view_guests.html', title="Guests", form=form, guests=guests)

@app.route('/view_work_orders', methods=['GET', 'POST'])
@login_required
def view_work_orders():
    form = ViewWorkOrderForm()
    # Get all reservations
    orders = db.session.query(WorkOrder, Employee).join(Employee, WorkOrder.employee_id == Employee.id).all()

    if form.validate_on_submit():
        new_orders = []
        # filter reservations based on inputted parameters
        for order in orders:
            if form.first_name.data.strip().lower() == "" or str(order[1].first_name).strip().lower() == form.first_name.data.strip().lower():
                if form.last_name.data.strip().lower() == "" or str(order[1].last_name).strip().lower() == form.last_name.data.strip().lower():
                    if form.room_num.data is None or order[0].room_num == form.room_num.data:
                        if form.type.data.strip().lower() == "" or str(order[0].type).strip().lower() == form.type.data.strip().lower():
                            new_orders.append(order)

        return render_template('view_work_orders.html', title="Work Orders", form=form, work_orders=new_orders)
    return render_template('view_work_orders.html', title="Work Orders", form=form, work_orders=orders)

@app.route('/edit_work_order/<work_order>', methods=['GET', 'POST'])
def edit_work_order(work_order):
    form = EditWorkOrderForm()
    order = WorkOrder.query.filter(WorkOrder.order_number == work_order).first()
    if form.validate_on_submit():
        comment = '\n' + str(date.today()) + ' - ' + form.comment.data
        order.comments = order.comments + comment
        db.session.commit()
        flash(f'You have added a comment to work order {work_order}!', 'success')
        return redirect(url_for('view_work_orders'))

    return render_template('edit_work_order.html', form = form, order = order)

@app.route('/delete_work_order/<work_order>', methods=['GET', 'POST'])
def delete_work_order(work_order):
    WorkOrder.query.filter(WorkOrder.order_number == work_order).delete()
    db.session.commit()
    flash(f'Work order {work_order} has been deleted!', 'success')
    return redirect(url_for('view_work_orders'))

@app.route('/vacate_room', methods=['GET', 'POST'])
def vacate_room():
    if not check_for_admin(current_user.admin_flag):
        flash(f'You must be an admin to access this page!','danger')
        return redirect(url_for('employee_portal'))
    form = VacateRoomForm()
    # Get all reservations
    reservations = Reservation.query.filter(Reservation.check_in <= get_int_date(date.today())).all()

    if form.validate_on_submit():
        new_reservations = []
        # filter reservations based on inputted parameters
        for res in reservations:
            if form.room_num.data is None or res.room_num == form.room_num.data:
                if form.phone.data.strip().lower() == "" or str(res.phone).strip().lower() == form.phone.data.strip().lower():
                    if form.email.data.strip().lower() == "" or str(res.email).strip().lower() == form.email.data.strip().lower():
                        if form.room_type.data.strip().lower() == "" or str(res.room_type).strip().lower() == form.room_type.data.strip().lower():
                            if form.check_in.data is None or res.check_in >= form.check_in.data:
                                if form.check_out.data is None or res.check_out <= form.check_out.data:
                                    new_reservations.append(res)

        return render_template('vacate_room.html', title="Vacate Room", form=form, reservations=new_reservations)
    return render_template('vacate_room.html', title="Vacate Room", form=form, reservations=reservations)

@app.route('/vacate_room/<reservation>/<room_num>', methods=['GET', 'POST'])
def vacate_room_helper(reservation, room_num):
    # Vacating room (deleting reservation and clearing room service requests)
    Reservation.query.filter(Reservation.id == reservation).delete()
    RoomService.query.filter(RoomService.room_num == room_num).delete()

    # Getting a random employee
    standard_employees = Employee.query.filter_by(admin_flag=0).all()
    employee_id = random.choice(standard_employees).id

    # Creating comment
    comment = str(date.today()) + ' - ' + 'Auto-generated room cleaning request'

    # Auto generating a cleaning request for vacated room
    cleaning_order = WorkOrder(type='Cleaning', room_num=room_num, employee_id=employee_id, comments=comment)
    db.session.add(cleaning_order)
    db.session.commit()
    flash(f'Room {room_num} has been vacated and room cleaning request has been generated!', 'success')
    return redirect(url_for('vacate_room'))


@app.route('/assign_room', methods = ['GET', 'POST'])
def assign_room():
    if not check_for_admin(current_user.admin_flag):
        flash(f'You must be an admin to access this page!','danger')
        return redirect(url_for('employee_portal'))

    form = ViewReservationsForm()
    # Get all reservations
    reservations = Reservation.query.all()

    if form.validate_on_submit():
        new_reservations = []
        # filter reservations based on inputted parameters
        for res in reservations:
            if form.first_name.data.strip().lower() == "" or str(
                    res.first_name).strip().lower() == form.first_name.data.strip().lower():
                if form.last_name.data.strip().lower() == "" or str(
                        res.last_name).strip().lower() == form.last_name.data.strip().lower():
                    if form.email.data.strip().lower() == "" or str(
                            res.email).strip().lower() == form.email.data.strip().lower():
                        if form.room_type.data.strip().lower() == "" or str(
                                res.room_type).strip().lower() == form.room_type.data.strip().lower():
                            if form.check_in.data is None or res.check_in >= form.check_in.data:
                                if form.check_out.data is None or res.check_out <= form.check_out.data:
                                    new_reservations.append(res)

        return render_template('assign_room.html', title="Assign Room", form=form, reservations=new_reservations)
    return render_template('assign_room.html', title="Assign Room", form=form, reservations=reservations)

@app.route('/edit_reservation/<id>', methods = ['GET', 'POST'])
def assign_room_helper(id):
    form = EditReservationForm()
    reservation = Reservation.query.filter(Reservation.id == id).first()
    num_guests = room_capacities[reservation.room_type]
    # Find open rooms
    room_counts, open_rooms, room_buckets = get_availability(num_guests, reservation.check_in, reservation.check_out)
    bisect.insort(room_buckets[reservation.room_type], reservation.room_num)
    room_counts[reservation.room_type] += 1

    if form.validate_on_submit():
        today = get_int_date(str(date.today()))
        # Validate dates
        if form.check_in.data is not None and form.check_out.data is not None:
            if form.check_in.data >= form.check_out.data:
                flash(f'Check in date cannot be after the check out date.', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            else:
                reservation.check_in = form.check_in.data
                reservation.check_out = form.check_out.data
        elif form.check_in.data is not None:
            # Validate check in date
            if form.check_in.data < today:
                flash(f'Check in date cannot be in the past.', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            elif form.check_in.data >= reservation.check_out:
                flash(f'New check in date cannot be after the current check out date. Please update the check out date as well.', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            else:
                reservation.check_in = form.check_in.data
        elif form.check_out.data is not None:
            # Validate check out date
            if form.check_out.data < today:
                flash(f'Check out date cannot be in the past.', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            elif form.check_out.data <= reservation.check_in:
                flash(f'New check out date cannot be before the current check in date. Please update the check in date as well.', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            else:
                reservation.check_out = form.check_out.data

        if form.room_type.data.strip().lower() != "":
            # Ensure the user picks an appropriate room number for the new room type
            if form.room_num.data is None and form.room_type.data.strip().lower() != reservation.room_type:
                flash(f'You must select an appropriate {reservation.room_type} room before changes can be saved.', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            else:
                reservation.room_type = form.room_type.data.strip().lower()

        # Update room availability based on new selections
        num_guests = room_capacities[reservation.room_type]
        room_counts, open_rooms, room_buckets = get_availability(num_guests, reservation.check_in, reservation.check_out)
        #bisect.insort(room_buckets[reservation.room_type], reservation.room_num)
        room_counts[reservation.room_type] += 1

        if form.room_num.data is not None:
            # Ensure chosen room number is available and of correct type
            if form.room_num.data not in room_buckets[reservation.room_type]:
                flash(f'Room number {form.room_num.data} is not available or is not a {reservation.room_type} room. Changes were not saved', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)
            else:
                reservation.room_num = form.room_num.data
        else:
            # NEED BETTER WAY OF CHECKING FOR CONFLICTS HERE
            # Check for conflicts with originally assigned room number
            if reservation.room_num not in room_buckets[reservation.room_type] :
                flash(f'Originally assigned room number {reservation.room_num} is not available during these dates. Changes were not saved', 'danger')
                return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)

        db.session.commit()
        flash('Changes have been made.', 'success')
        return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)

    flash(f'The system has assigned reservation {reservation.id} to room {reservation.room_num}', 'success')
    return render_template('edit_reservation.html', form=form, res=reservation, counts=room_counts, room_buckets=room_buckets)

@app.route('/<filename>')
def load_image(filename):
    return send_from_directory('static/', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500

# used to check admin status
def check_for_admin(admin_flag):
    if admin_flag == False:
        return False
    else:
        return True
