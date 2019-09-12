import os
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def InternalServerError(e):
    home_files, face_files, text, confs = FaceClassification.generate_home()
    return render_template('index.html', title='Home', examples=home_files, face_files=face_files, text=text), 500

if __name__ == "__main__":
    app.run('localhost', port=5555)