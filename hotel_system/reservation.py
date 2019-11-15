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
