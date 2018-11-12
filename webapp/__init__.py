from flask import Flask, render_template, flash, request, redirect, url_for, session, escape
from content_management import Content
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os


TOPIC_DICT = Content()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
@app.route('/main/')
def homepage():
    return render_template("main.html")

@app.route('/home/')
def home():
	#flash("flash test!!!!")
    return render_template("home.html", TOPIC_DICT = TOPIC_DICT)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def page_not_found(e):
	return render_template("405.html")

# @app.route('/hom/')
# def slashboard():
# 	try:
# 		return render_template("home.html", TOPIC_DICT = shamwow)
# 	except Exception as e:
# 		return render_template("500.html", error= str(e))


@app.route('/login/', methods = ["GET", "POST"])
def login_page():
	try:
		error = ''

		c, conn = connection()
		if request.method == 'POST':
			username = thwart(request.form['username']).decode()
			data = c.execute('SELECT * FROM users WHERE username = ("%s");' % username)
			data = c.fetchone()


			if sha256_crypt.verify(request.form['password'], data[2]) and (data[1] == username):
				session['logged_in'] = True
				session['username'] = username
				flash('You are now logged in')
				return redirect(url_for('home'))
			else:
				error = 'Invalid credentials, try again'
		gc.collect()
		return render_template('login.html', error = error)
	except Exception as e:
		error = 'Invalid credentials, try again'
		return render_template('login.html', error = error)
#To DO (change password?)

# @app.route('/logout/')
# @login_required
# def logout_page():
# 	if session['logged_in']:
# 		session['logged_in'] = False
# 		session['username'] = None
# 	return redirect(url_for('main'))

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = TextField('Password', [validators.Required(),
                                        validators.EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the<a href="/tos/" Terms of Service</a> and the <href="/privacy/"Privacy Notice</a>, last updated Nov 8, 2018', [validators.Required()])


@app.route('/register/', methods = ["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.hash((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                            (thwart(username),))

            if int(x) > 0:

                return render_template('register.html', form = form)

            else:
                c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                            (thwart(username), thwart(password), thwart(email)))
                             
                conn.commit()
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for("home"))

        return render_template("register.html", form = form)
    except Exception as e:
        return(str(e))

if __name__ == "__main__":
	# app.secret_key = os.urandom(24)
	app.run()

#home is dashboard