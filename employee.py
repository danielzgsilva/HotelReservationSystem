import sqlite3 as sql

class Employee:
    def __init__(self, first_name, last_name, email, password, role):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

        if role == 'Admin':
            self.admin_flag = 'TRUE'
        else:
            self.admin_flag = 'FALSE'


    def store(self):
        # Connect to database
        conn = sql.connect('database/HotelDB.db')
        cur = conn.cursor()

        try:
            # Create row to be inserted into employees table
            employee = (self.first_name, self.last_name, self.email, self.password, self.admin_flag)

            # Insert row of data into database
            cur.execute('INSERT INTO Employees VALUES {}'.format(employee))
            conn.commit()

            # close connection
            conn.close()
            return True
        except():
            conn.close()
            return False
