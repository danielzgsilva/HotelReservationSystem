import sqlite3 as sql
from datetime import datetime

room_capacities = {'single': 2, 'double': 4, 'deluxe': 6}
prices = {'single': 90, 'double': 150, 'deluxe': 250}

def get_int_date(date):

    # dates are inputted in this format: 2019-09-17
    if isinstance(date, int):
        return date

    # need to put in int format: 09170219
    date = int(str(date).replace('-', ''))

    return date

class temp_reservation:
    def __init__(self, check_in, check_out, room_type):
        self.check_in = check_in
        self.check_out = check_out
        self.room_type = room_type

        # Price per night depending on room selection
        self.price_per_night = prices[self.room_type]

        # Calculate length of stay
        delta = datetime.strptime(check_out, "%Y-%m-%d").date() - datetime.strptime(check_in, "%Y-%m-%d").date()
        self.length = delta.days

def get_availability(num_guests, date_in, date_out):
    # Connect to database
    conn = sql.connect('hotel_system/HotelDB.db')
    cur = conn.cursor()

    # Create query which will search the reservations table for open rooms
    query = ('select room_num, room_type from room where '
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
    cur.execute(query)
    rooms = cur.fetchall()
    counts = {'single': 0, 'double': 0, 'deluxe': 0}
    room_buckets = {'single': [], 'double': [], 'deluxe': []}

    # Counting the number of rooms available, for each room type
    for room in rooms:
        counts[room[1]] += 1
        room_buckets[room[1]].append(room[0])

    conn.close()
    # Return availability
    return counts, rooms, room_buckets
