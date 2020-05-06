from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

# Packages In our project
from project.database import connect, verifyUser, checkUser, alreadyAnUser, isUnverified, getCurrentUser
from project.forms import loadForm, checkEmptyForm

app = Flask(__name__)
app.secret_key = 'csc394team3_jgdjd5dd56eyjr67e56'

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'team3csc394@gmail.com',
    "MAIL_PASSWORD": 'zjpijhdslwwfrkba'
}

app.config.update(mail_settings)

mail = Mail(app)

@app.route('/', methods=['POST', 'GET'])
def index():
	try:
		user = session['user_hash']
		if user:
			return redirect(url_for('home'))
		else:
			return redirect(url_for('login'))
	except Exception as e:
		return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
	user = session['user_hash']
	if user:
		return redirect(url_for('home'))

	form_dict = {}
	errors = []
	success = []

	if request.method == 'POST':
		# Get data from form
		form_dict = loadForm(form_dict)
		# Make sure fields are not empty
		noErrors = checkEmptyForm(form_dict)
		if noErrors:
			email = form_dict['email']
			first_name = form_dict['first_name']
			last_name = form_dict['last_name']
			password = generate_password_hash(form_dict['password'])
			confirm_password = form_dict['confirm_password']
			
			perm = 1
			position_id = 1

			user_hash = generate_password_hash(str(email) + str(first_name) + str(last_name) + str(password))

			# Validate As Needed
			if form_dict['password'] != confirm_password:
				errors.append("Passwords do not Match.")

			if alreadyAnUser(email):
				errors.append("There is already an user with that email address.")
			# If no errors, proceed with database interaction
			if len(errors) == 0:
				sql = "INSERT INTO users (email, first_name, last_name, password, permission_id, position_id, user_hash, verified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
				data = [email, first_name, last_name, password, perm, position_id, user_hash, 0]
				db, cursor = connect()
				try:
					cursor.execute(sql, data)
					db.commit()
					db.close()
					registration = "<p>Thank you for signing up. Please click the link to verify.</p><br>"
					registration += "<p><a href='http://127.0.0.1:5000/confirm?user="+str(user_hash)+"'>Verify</a></p>"
					msg = Message(subject='Verify Email - CSC 394', html=registration, sender="webappforcsc394@gmail.com", recipients=["team3csc394@gmail.com"]) # ENTER YOUR EMAIL IN recipients
					mail.send(msg)
					success.append("You have been signed up. Please check your Email to verify your account.")
				except Exception as e:
					errors.append("Exception found: " + str(e))
			else:
				print("There Was an Error.")
		else:
			errors.append('There are empty fields in the form.')
	return render_template('register.html', errors=errors, success=success)

@app.route('/home', methods=['POST', 'GET'])
def home():
	errors = []
	messages = []

	user = session['user_hash']
	user = getCurrentUser(user)
	if user:
		if isUnverified(user['email']):
			messages.append("Please Verify your email address!")
	else:
		return redirect(url_for('login'))
	return render_template('home.html', user=user, messages=messages)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
	session['user_hash'] = None
	return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
	try:
		user = session['email']
		if user:
			return redirect(url_for('home'))
	except Exception as e:
		pass

	form_dict = {}
	errors = []

	if request.method == 'POST':
		# Get data from form
		form_dict = loadForm(form_dict)
		email = form_dict['email']
		password = form_dict['password']
		if checkUser(email, password):
			user = getCurrentUser(None,email=email)
			session['user_hash'] = user['user_hash']
			return redirect(url_for('home'))
		else:
			errors.append("Email or Password is Incorrect. Try Again.")

	return render_template('login.html', errors=errors)

@app.route('/confirm', methods=['POST', 'GET'])
def confirm():
	user = request.args.get('user')
	if verifyUser(user):
		return 'User verified. <p><a href="http://127.0.0.1:5000/login">Login</a></p>'
	else:
		return 'Invalid User. <p><a href="http://127.0.0.1:5000/">Return Home</a></p>'

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

if __name__ == "__main__":
	app.run(debug=True)
