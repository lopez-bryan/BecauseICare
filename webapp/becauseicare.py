from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
@app.route('/signin.html')
def sign_in() -> 'html':
	return render_template('signin.html', the_title = 'Because I Care')


if __name__ == '__main__':
	app.run(debug = True)