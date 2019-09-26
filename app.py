import os
from flask import Flask, render_template, send_from_directory, request

import QueryDB

app = Flask(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html', title='Home', single_count = -1, double_count = -1, deluxe_count = -1)

@app.route('/check_availability', methods=['GET', 'POST'])
def check_availability():
    # Get user Input
    num_guests = int(request.form.get('guest_num_input'))
    check_in = str(request.form.get('check_in'))
    check_out = str(request.form.get('check_out'))

    date_in = QueryDB.get_int_date(check_in)
    date_out = QueryDB.get_int_date(check_out)

    # Querying hotel database
    single_count, double_count, deluxe_count = QueryDB.get_availability(num_guests, date_in, date_out)

    return render_template('available_rooms.html', single_count = single_count, double_count = double_count, deluxe_count = deluxe_count)

@app.route('/<filename>')
def load_image(filename):
    return send_from_directory('static/', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500

if __name__ == "__main__":
    app.run('localhost', port=5555)