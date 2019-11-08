import sqlite3 as sql

def get_int_date(date):

    # dates are inputted in this format: 2019-09-17
    data = date.split('-')

    # need to put in int format: 09170219
    int_date = int(data[1] + data[2] + data[0])

    return int_date

def get_availability(num_guests, date_in, date_out):
    # Connect to database
    conn = sql.connect('HotelDB.db')
    cur = conn.cursor()

    # Create query which will search the reservations table for open rooms
    query = ('select * from room where '
             '{} <= capacity and not exists '
             '(select 1 from reservation where '
             'room.room_num = reservation.room_num '
             'and'
             '({} between check_in and check_out '
             'or '
             '{} between check_in and check_out '
             'or '
             'check_in between {} and {} '
             'or '
             'check_out between {} and {}))'.format(num_guests, date_in, date_out, date_in, date_out, date_in, date_out))

    single_count = 0
    double_count = 0
    deluxe_count = 0

    # Counting the number of rooms available, for each room type
    for row in cur.execute(query):
        if row[1] == 'Single':
            single_count += 1
        elif row[1] == 'Double':
            double_count += 1
        elif row[1] == 'Deluxe':
            deluxe_count += 1
    conn.close()
    # Return availability
    return single_count, double_count, deluxe_count
