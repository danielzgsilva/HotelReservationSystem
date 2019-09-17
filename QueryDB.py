import sqlite3 as sql

def get_availability(num_guests, date_in, date_out):
    conn = sql.connect('database/HotelDB.db')
    cur = conn.cursor()

    query = ('select * from rooms where '
             '{} <= capacity and not exists '
             '(select 1 from Reservations where '
             'Rooms.Number = Reservations.Room_Num '
             'and'
             '({} between Check_In and Check_Out '
             'or '
             '{} between Check_In and Check_Out '
             'or '
             'Check_In between {} and {} '
             'or '
             'Check_Out between {} and {}))'.format(num_guests, date_in, date_out, date_in, date_out, date_in, date_out))

    single_count = 0
    double_count = 0
    deluxe_count = 0

    for row in cur.execute(query):
        if row[1] == 'Single':
            single_count += 1
        elif row[1] == 'Double':
            double_count += 1
        elif row[1] == 'Deluxe':
            deluxe_count += 1

    return single_count, double_count, deluxe_count

def get_int_date(date):

    # dates are inputted in this format: 2019-09-17
    data = date.split('-')

    # need to put in int format: 09170219
    int_date = int(data[1] + data[2] + data[0])

    return int_date