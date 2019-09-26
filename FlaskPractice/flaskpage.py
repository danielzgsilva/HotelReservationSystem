from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '0050e31e5bb1947eef641bee2b1c871b'

posts = [
    {
        'author':'rodrigo lopez',
        'title':'blog post 1',
        'content':'first post content',
        'date_posted':'April 20, 2019'
    },
    {
        'author':'sydney toolis',
        'title':'blog post 2',
        'content':'second post content',
        'data_posted':'April 21, 2019'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = "Register", form = form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #fake data for now to simulate log in
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash(f'You Have Been Loged In!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title = "Login", form = form)


# this is used to run in the interpreter
if __name__ == '__main__':
    app.run(debug=True)
