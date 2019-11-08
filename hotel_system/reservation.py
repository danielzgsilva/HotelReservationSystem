import sqlite3 as sql
from hotel_system.utils import get_int_date
from datetime import datetime

class Reservation:
    def __init__(self, check_in, check_out, room_type):
        self.check_in = check_in
        self.check_out = check_out
        self.room_type = room_type

        # Price per night depending on room selection
        prices = {'single': 90, 'double': 150, 'deluxe': 250}
        self.price_per_night = prices[self.room_type]

        # Calculate length of stay
        delta = datetime.strptime(check_out, "%Y-%m-%d").date() - datetime.strptime(check_in, "%Y-%m-%d").date()
        self.length = delta.days

    def store_reservation(self, first_name, last_name, email, phone, wifi, tv, parking, pool):
        # Creating integer dates for database
        date_in = get_int_date(self.check_in)
        date_out = get_int_date(self.check_out)

        # Checking additional feature checkboxes
        if wifi is None:
            wifi = 'FALSE'
        if tv is None:
            tv = 'FALSE'
        if parking is None:
            parking = 'FALSE'
        if pool is None:
            pool = 'FALSE'

        # Connect to database
        conn = sql.connect('database/HotelDB.db')
        cur = conn.cursor()

        # Create row to be inserted into reservations table
        reservation = (first_name, last_name, wifi, tv, parking, pool, phone, email, date_in, date_out, self.room_type, 0)

        # Insert row of data into database
        cur.execute('INSERT INTO Reservations VALUES {}'.format(reservation))
        conn.commit()

        # close connection
        conn.close()
        return

    @staticmethod
    def get_availability(num_guests, date_in, date_out):
        # Connect to database
        conn = sql.connect('database/HotelDB.db')
        cur = conn.cursor()

        # Create query which will search the reservations table for open rooms
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
