import os
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html')

@app.route('/<filename>')
def load_image(filename):
    return send_from_directory('static/', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500

if __name__ == "__main__":
    app.run('localhost', port=5555)