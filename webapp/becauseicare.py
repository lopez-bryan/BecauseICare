# from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os

app = Flask(__name__)

# @app.route('/')
# @app.route('/signin.html')
# def sign_in() -> 'html':
# 	return render_template('signin.html', the_title = 'Because I Care')

 
# app = Flask(__name__)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('signin.html', the_title = 'Because I Care')
    else:
        return "Hello Boss!"
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return render_template('main.html', the_title = 'Because I Care')
    else:
        flash('wrong password!')
    return render_template('newuser.html', the_title = 'Because I Care', the_instruction = "Create a new user")
    # return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route('/newuser')
def newuser():
	return render_template('newuser.html', the_title = 'Because I Care')

# def log_request(req: 'flask_request', sep: str) ->None:
# 	"""Log details into database"""
# 	dbconfig = { 'host': '127.0.0.1',
# 				 'user': 'vsearch',
# 				 'password': 'vsearchpasswd',
# 				 'database': 'vsearchlogDB', }
# 	conn = mysql.connector.connect(**dbconfig)
# 	cursor = conn.cursor()

# 	_SQL = """INSERT INTO log
# 			(phrase, letters, ip, browser_string, results)
# 			VALUES(%s, %s, %s, %s, %s)"""
# 	cursor.execute(_SQL, (req.form['phrase'],
# 						  req.form['letters'],
# 						  req.remote_addr,
# 						  req.user_agent.browser,
# 						  res, ))
# 	conn.commit()
# 	cursor.close()
# 	conn.close()
@app.route('/main')
def main_page() -> 'html':
	return render_template('main.html', the_title = 'Because I Care')

@app.route('/addingItem')
def adding_Item() -> 'html':
	"""This is the main page where I will make my lists."""
	addItem = req.form['addItem']
	return render_template('main.html', the_title = 'Because I Care', 
										add_Item = addItem)

"""possible code to retrieve data from database"""
# cur = con.cursor()
# cur.execute("SELECT * FROM dataset")
# data = cur.fetchall()
# render_template('template.html', data=data)
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug = True)
    # app.run(debug=True,host='0.0.0.0', port=5000)






# if __name__ == '__main__':
# 	app.run(debug = True)