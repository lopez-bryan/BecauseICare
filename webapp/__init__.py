from flask import Flask, render_template, flash, request, redirect, url_for, session, escape
from content_management import Content
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os
from functools import wraps


TOPIC_DICT = Content()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
@app.route('/main/')
def homepage():
    return render_template("main.html")

@app.route('/home/')
def home():
	c, conn = connection()
	_ = c.execute('SELECT item FROM items ORDER BY item DESC;')
	contents = c.fetchall() 
	title = 'NEEDS'
	c.close()
	conn.close()
	gc.collect()
	#second table
	c, conn = connection()
	_ = c.execute('SELECT finished_item FROM items')#-
	finished_items = c.fetchall() 
	finished_title = 'NEEDS MET'
	c.close()
	conn.close()
	gc.collect()
	#flash("flash test!!!!")
	return render_template("home.html",TOPIC_DICT = TOPIC_DICT,the_contents = contents,the_title = title,finished_items= finished_items, finished_title= finished_title)

# @app.route('/home/')
# def home():
# 	c, conn = connection()
# 	_ = c.execute('SELECT item FROM items WHERE finished_item != "finished" ORDER BY item DESC;')
# 	contents = c.fetchall() 
# 	title = 'NEEDS'
# 	# finished_title = 'NEEDS MET'
# 	c.close()
# 	conn.close()
# 	gc.collect()
# 	#second table
# 	# c, conn = connection()
# # 	_ = c.execute('SELECT finished_item FROM items')#-
# # 	finished_items = c.fetchall() 
# # 	finished_title = 'NEEDS MET'
# # 	c.close()
# # 	conn.close()
# # 	gc.collect()
# 	#flash("flash test!!!!")
# 	return render_template("home.html",TOPIC_DICT = TOPIC_DICT,the_contents = contents,the_title = title,finished_items= finished_items, finished_title= finished_title)

        
@app.route('/itemUpdate', methods = ['POST'])
def completed_item():
	if request.method == 'POST':
		movedItem = request.form.getlist("item")

		c, conn = connection()
		for item in movedItem:
			c.execute('DELETE FROM items WHERE item == ("%s");' %
                            (item))
			conn.commit()
		c.close()
		conn.close()
		gc.collect()

		return redirect(url_for("home"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def page_not_found(e):
	return render_template("405.html")

@app.route(TOPIC_DICT["Basics"][0][1])
def go_to_adding_item():
    return render_template("addItem.html")


@app.route('/addItem', methods = ['POST'])
# @login_required
def addingItem():
    if request.method == 'POST':
        yourItem = thwart(request.form['yourItem'])
        c, conn = connection()
        c.execute('INSERT INTO items (item) VALUES ("%s");' %
                            (yourItem))
    conn.commit()
    c.close()
    conn.close()
    gc.collect()

    return redirect(url_for("home"))


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

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap

@app.route("/logout/")
@login_required
def logout():
	session.clear()
	flash("You have been logged out!")
	gc.collect()
	return redirect(url_for('main'))
		

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

                return redirect(url_for("login_page"))

        return render_template("register.html", form = form)
    except Exception as e:
        return(str(e))

@app.route('/support-donate/')
def donate():
	donate = "Donations!"
	return render_template("support-donate.html", donate = donate)

if __name__ == "__main__":
	# app.secret_key = os.urandom(24)
	app.run(debug = True)

#home is dashboard