from flask import Flask, render_template, flash, request, redirect, url_for, session, escape
from content_management import Content
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os, logging
from functools import wraps
from flask_login import login_manager, login_required, logout_user
from flask_mail import Mail, Message


#naming the variable that holds my Content function I imported
TOPIC_DICT = Content()

#Start of the app. I have configured email settings that are not working at the moment. So 
# I deleted the password since I'm pushing this to GitHub. I also have set my secret_key to random
app = Flask(__name__)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'bryanjlopez01@gmail.com',
	MAIL_PASSWORD = '/'
	)
mail = Mail(app)
app.secret_key = os.urandom(24)


#I put my landing route together with my landing page I called main. It's just a way to double check.
@app.route('/')
@app.route('/main/')
def homepage():
    return render_template("main.html")
    

#Home route is the most interactive for the user. Here they see a list, delete from the list, go to
#the add item page, and possibly go to a forum which hasn't been created yet.
@app.route('/home/')
def home():
	c, conn = connection()
	#Pulls down all the items on the list by the most recent at the top.
	_ = c.execute('SELECT item FROM items ORDER BY dt DESC;')
	contents = c.fetchall() 
	title = 'NEEDS'
	c.close()
	conn.close()
	gc.collect()
	#second table
	c, conn = connection()
	#A second list for the items to go to. Currently isn't working at the moment.
	_ = c.execute('SELECT finished_item FROM items')#-
	finished_items = c.fetchall() 
	finished_title = 'NEEDS MET'
	c.close()
	conn.close()
	gc.collect()
	#flash("flash test!!!!")
	return render_template("home.html",TOPIC_DICT = TOPIC_DICT,the_contents = contents,the_title = title,finished_items= finished_items, finished_title= finished_title)


#Function to make sure a user is logged in if they want to interact with things like adding items.
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))
    return wrap


#This grabs the items that are checked in the checkbox and deletes them from the database and list. 
@app.route('/itemUpdate', methods = ['GET','POST'])
@login_required
def completed_item():
	if request.method == 'POST':
		movedItem = request.form.getlist("item")
		
		c, conn = connection()
		for item in movedItem:
			c.execute('DELETE FROM items WHERE item = ("%s");' %
                            (item))
		conn.commit()
		c.close()
		conn.close()
		gc.collect()

		return redirect(url_for("home"))


#Error page to handle 404. I don't wan't the user to see my errors if they happen to.
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


#Error page to handle 505. User shouldn't see error as they would help unwanted hackers.
@app.errorhandler(405)
def page_not_found(e):
	return render_template("405.html")


#Route for link to adding items. I currently don't have one for forums yet.
@app.route(TOPIC_DICT["Basics"][0][1])
def go_to_adding_item():
    return render_template("addItem.html")


#This makes sure user is logged in and retrieves item to be added and puts it in the database.
@app.route('/addItem', methods = ['POST'])
@login_required
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


#Route collects username and password and checks the database to see if they match. If they do, the
#user is logged in successfully. If they don't, the user is sent to the register page.
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


#Route logs the user out and clears the session.
@app.route("/logout/")
@login_required
def logout():
	session.clear()
	flash("You have been logged out!")
	gc.collect()
	return redirect(url_for("homepage"))


#Form to securely check and validate usernames and password. The user must also check the tos box.
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = TextField('Password', [validators.Required(),
                                        validators.EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the<a href="/tos/" Terms of Service</a> and the <href="/privacy/"Privacy Notice</a>, last updated Nov 8, 2018', [validators.Required()])


#Route to register new users.
@app.route('/register/', methods = ["GET", "POST"])
def register_page():
	#using error catching to make it more secure.
    try:
        form = RegistrationForm(request.form)
		#Pulling data from the form and validating it to make more secure
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            #Using password hashing to encrypt the passwords in the database
            password = sha256_crypt.hash((str(form.password.data)))
            c, conn = connection()
			
			#Checking all of the usernames in the database.
            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                            (thwart(username),))
			#If any usernames already exists in the database, the page will return to register users.
            if int(x) > 0:

                return render_template('register.html', form = form)
			#Otherwise, the username, password, and email will be put into the database.
            else:
                c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                            (thwart(username), thwart(password), thwart(email)))
                             
                conn.commit()
                c.close()
                conn.close()
                gc.collect()
				#When user is logged in, the session and username are set.
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for("login_page"))

        return render_template("register.html", form = form)
    except Exception as e:
        return(str(e))


# Route to donations.
@app.route('/support-donate/')
def donate():
	donate = "Donations!"
	return render_template("support-donate.html", donate = donate)


#Route to terms of service
@app.route('/about/tos/')
def tos():
	tos = "Terms of Service"
	return render_template("about/tos.html", tos = tos)


#Route to privacy policy
@app.route('/about/privacy-policy/')
def tos():
	privacy = "Privacy Policy"
	return render_template("about/privacy-policy.html", privacy = privacy)
	

#route to contact me for hire.
@app.route('/consulting/')
def consulting():
	consulting = "Hire me or ask questions"
	return render_template("consulting.html", consulting = consulting)


#To send emails to users
#TODO
#Might add send mail to group option
# @app.route('/send-mail/')
# def send_mail():
# 	try:
# 		msg = Message("Welcome to Because We Cares!",
# 		  sender="bryanjlopez01@gmail.com",
# 		  #recipients is who is getting mail
# 		  recipients=["recievingemail@email.com"])
# 		msg.body = "Hello,\nI just want to welcome you to BecauseWeCares.com."           
# 		mail.send(msg)
# 		return 'Mail sent!'

# 	except Exception, e:
# 		return(str(e))


# Possible sending mail. 
@app.route('/send-mail/')
def send_mail():
	try:
		msg = Message("Forgot Password - BecauseWeCares.com",
		  sender="bryanjlopez01@gmail.com",
		  #recipients is who is getting mail
		  recipients=[username])
		msg.body = 'Hello '+username+',\nYou or someone else has requested that a new password be generated for your account. If you made this request, then please follow this link:'+link
		msg.html = render_template("main.html", username=username, link=link)

		mail.send(msg)
		return 'Mail sent!'

	except Exception, e:
		return(str(e))


#forgot password route
@app.route('/forgot-password/')
def forgot_password():
	return render_template("/mails/reset-password.html")

	
#This goes with the addItem.html. It connects to the database and pulls all the users out of it.
#Then the JavaScript allows the user to select which other users to add the item to.
@app.route('/users/')
def users():
	c, conn = connection()
	c.execute('select username from users')
	data = c.fetchall()
	conn.commit()
	c.close()
	conn.close()
	gc.collect()
	users = []
	for user in data:
		users.append(user[0])
	return str(users)


if __name__ == "__main__":
	app.run()