from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from ast import literal_eval as make_tuple
# Packages In our project
from project.database import connect, verifyUser, checkUser,\
							alreadyAnUser, isUnverified, getCurrentUser, \
							getUserPermission, currentUser, getAllPermissions, \
							getAllPositions, getSiteURL, getColumns, getAllGroups, \
							getUsersByGroups, getAllUsers,addUser,deleteUser,getUserGroups, \
							getGroupMembers, getKanbanCards, getKanbanCard, moveKanbanCard, \
							getAllPositions, getSiteURL, getColumns, getAllGroups, getUsersByGroups, getAllUsers,addUser,deleteUser,getUserGroups,getUserHash, getKanbanCardComments, getCardsByGroup

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
site_url = getSiteURL()

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

app.route('/grouplist', methods=['POST', 'GET'])
def grouplist():
	print("here")
@app.route('/groups', methods=['POST', 'GET'])
def groups():
	form_dict = {}
	errors = []
	success = []
	user = session['user_hash']
	user = getCurrentUser(user)
	users = getAllUsers()
	groups = getAllGroups(user['user_hash'])
	if request.method == 'POST':
		# Get data from form
		print(request.form)
		if "team" in request.form:
			sql = "INSERT INTO groups (g_name,owner) VALUES (%s, %s)"
			data = [request.form['team'],user['user_hash']]
			db, cursor = connect()
			try:
				cursor.execute(sql, data)
				db.commit()
				db.close()
				success.append("Successfully Created Group")
				groups = getAllGroups(user['user_hash'])
			except Exception as e:
				errors.append("Exception found: " + str(e))
			
			return render_template('groups.html', groups = groups, users = users, errors=errors, success=success)
		if "addusers" in request.form:
			gids = getUserGroups(request.form['names'])
			
			for i in gids:
				print(request.form['gid'])
				print(i['g_id'])
				if int(request.form['gid']) == int(i['g_id']):
					users = getAllUsers()
					errors.append("was already in that group")
					return render_template('groups.html', groups = groups, users = users, errors=errors, success=success)
			

			print(request.form['gid'])
			deleteUser(request.form['gid'],request.form['names'])
			addUser(request.form['gid'],request.form['names'])
			users = getAllUsers()
			success.append("Successfully Added User to Group")
			return render_template('groups.html', groups = groups, users = users, errors=errors, success=success)
		else:
			form_dict = request.form['sub']
			names = getUsersByGroups(form_dict);
			return render_template('grouplist.html', team = names)
		
	
	return render_template('groups.html', groups = groups, users = users, errors=errors, success=success)



@app.route('/grouplist', methods=['POST', 'GET'])
def grouplist():
	errors = []
	success = []
	print("here")

	tupes = (request.form['names'].split(","))
	print(tupes)
	print (tupes[0])
	hashs  = getUserHash(tupes[2])
	print(hashs)

	sql = "DELETE FROM user_groups WHERE g_id = %s and user = %s"
	data = [tupes[0],hashs[0]['user_hash']]
	db, cursor = connect()
	try:
		cursor.execute(sql, data)
		db.commit()
		db.close()
		print("deleeted")
		success.append("Successfully Created Group")
	except Exception as e:
		errors.append("Exception found: " + str(e))
	names = getUsersByGroups(tupes[0]);
	return render_template('grouplist.html', team = names)

@app.route('/register', methods=['POST', 'GET'])
def register():
	form_dict = {}
	errors = []
	success = []

	try:
		user = session['user_hash']
		if user:
			return redirect(url_for('home'))
	except Exception as e:
		pass

	if request.method == 'POST':
		# Get data from form
		form_dict = loadForm(form_dict)
		# Make sure fields are not empty
		empty = checkEmptyForm(form_dict)
		if not empty:
			email = form_dict['email']
			first_name = form_dict['first_name']
			last_name = form_dict['last_name']
			password = generate_password_hash(form_dict['password'])
			confirm_password = form_dict['confirm_password']
			
			perm = 1
			position_id = 1

			user_hash = generate_password_hash(str(email) + str(first_name) + str(last_name) + str(password))
			organization = generate_password_hash(str(user_hash))

			# Validate As Needed
			if form_dict['password'] != confirm_password:
				errors.append("Passwords do not Match.")

			if alreadyAnUser(email):
				errors.append("There is already an user with that email address.")
			# If no errors, proceed with database interaction
			if len(errors) == 0:
				sql = "INSERT INTO users (email, first_name, last_name, password, permission_id, position_id, user_hash, verified, organization) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
				data = [email, first_name, last_name, password, perm, position_id, user_hash, 0, organization]
				db, cursor = connect()
				try:
					cursor.execute(sql, data)
					db.commit()
					db.close()
					registration = "<p>Thank you for signing up. Please click the link to verify.</p><br>"
					registration += "<p><a href='"+str(site_url)+"confirm?user="+str(user_hash)+"'>Verify</a></p>"
					msg = Message(subject='Verify Email - CSC 394', html=registration, sender="webappforcsc394@gmail.com", recipients=[str(email)]) # ENTER YOUR EMAIL IN recipients
					mail.send(msg)
					success.append("You have been signed up. Please check your Email to verify your account.")
				except Exception as e:
					errors.append("Exception found: " + str(e))
			else:
				print("There Was an Error.")
		else:
			errors.append('There are empty fields in the form.')
	return render_template('register.html', current_data=None, errors=errors, success=success)

@app.route('/archives', methods= ['POST', 'GET'])
def archives():
	user = session['user_hash']
	user = getCurrentUser(user)
	cards = []
	if user:
		groups = getUserGroups(user['user_hash'])
		for g in groups:
			for c in getCardsByGroup(g['g_id']):
				cards.append(c)

	return render_template('archives.html', cards = cards)

@app.route('/user', methods= ['POST', 'GET'])
def user():
	user = session['user_hash']
	user = getCurrentUser(user)

	return render_template('user.html',fname = user['first_name'] ,lname= user['last_name'] , email= user['email'] , perm=user['permission'] )
	
@app.route('/home', methods=['POST', 'GET'])
def home():
	errors = []
	messages = []

	user = session['user_hash']
	user = currentUser(user)

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
		return 'User verified. <p><a href="'+str(site_url)+'login">Login</a></p>'
	else:
		return 'Invalid User. <p><a href="'+str(site_url)+'">Return Home</a></p>'

@app.route('/account', methods=['POST', 'GET'])
def account():
	user = session['user_hash']
	user = currentUser(user)
	if user:
		return render_template('account.html', user=user)
	else:
		return redirect(url_for('login'))

@app.route('/kanban', methods=['POST', 'GET'])
def kanban():
	user = session['user_hash']
	user = currentUser(user)
	kanbans = {}
	if user:
		user_groups = getUserGroups(user['user_hash'])
		for group in user_groups:
			members = getGroupMembers(group['g_id'])
			kanbans[group['g_id']] = {}
			kanbans[group['g_id']]['members'] = members
			kanbans[group['g_id']]['title'] = group['g_name']
			kanbans[group['g_id']]['cards'] = {}
			kanbans[group['g_id']]['cards']['todo'] = getKanbanCards(group['g_id'], 'todo')
			kanbans[group['g_id']]['cards']['inprogress'] = getKanbanCards(group['g_id'], 'inprogress')
			kanbans[group['g_id']]['cards']['complete'] = getKanbanCards(group['g_id'], 'complete')

		return render_template('kanban.html', user=user, kanbans=kanbans)
	else:
		return redirect(url_for('login'))

@app.route('/kanban/card/<card_number>', methods=['POST', 'GET'])
def kanban_card(card_number):
	user = session['user_hash']
	user = currentUser(user)
	success = []
	errors = []
	if user:
		card = getKanbanCard(card_number)
		comments = getKanbanCardComments(card_number)
		print(comments)
		return render_template('kanban_card.html', user=user, errors=errors, success=success, card=card, comments=comments)
	else:
		return redirect(url_for('login'))

@app.route('/kanban/card/comment', methods=['POST', 'GET'])
def kanban_card_comment():
	user = session['user_hash']
	user = currentUser(user)
	sql = "INSERT INTO card_comments (card_id, user, comment) VALUES (%s, %s, %s)"
	if request.method == 'POST':
		comment = request.form['comment']
		card_id = request.form['card_id']
		if comment and comment != '' and comment != ' ':
			db, cur = connect()
			cur.execute(sql, [card_id, user['user_hash'], comment])
			db.commit()
			db.close()
			return redirect('http://127.0.0.1:5000/kanban/card/'+str(card_id), code=302)
	return redirect('http://127.0.0.1:5000/kanban/card/'+str(card_id), code=302)


@app.route('/kanban/card/edit', methods=['POST', 'GET'])
def kanban_card_edit():
	form_dict = {}
	form_dict = loadForm(form_dict)
	form_dict['completed'] = '1' if len(request.form.getlist('completed')) > 0 else '0'
	sql = """
			UPDATE cards
			SET
				title = %s,
				description = %s,
				completed = %s,
				due_date = %s,
				archived = %s
			WHERE id = %s
		  """
	data = [form_dict['title'], form_dict['description'], form_dict['completed'], form_dict['due_date'], form_dict['archived'], form_dict['card_id']]
	db,cur = connect()
	cur.execute(sql, data)
	db.commit()
	db.close()
	return redirect('/kanban/card/' + str(form_dict['card_id']))

@app.route('/kanban/card/move', methods=['POST', 'GET'])
def kanban_move_card():
	card_id = request.args.get('card')
	destination = request.args.get('destination')
	moveKanbanCard(card_id, destination)
	return redirect(url_for('kanban'))

@app.route('/kanban/add_card', methods=['POST', 'GET'])
def kanban_add_card():
	user = session['user_hash']
	user = currentUser(user)
	group_id = request.args.get('group')
	category = request.args.get('category')
	members = getGroupMembers(group_id)
	form_dict = {}
	errors = []
	success = []

	if request.method == 'POST':
		form_dict = loadForm(form_dict)
		empty = checkEmptyForm(form_dict)

		if empty:
			errors.append("There are empty fields! Please Complete")
		else:
			db,cur = connect()
			sql = "INSERT INTO cards (title, description, assigned_to, kanban_category, group_id, completed, owner, due_date, archived) VALUES (%s, %s,%s, %s,%s, %s,%s,%s,%s)"
			title = form_dict['title']
			description = form_dict['description']
			assigned_to = form_dict['assigned_to']
			kanban_category = form_dict['kanban_category']
			due_date = form_dict['due_date']
			completed =form_dict['completed']
			owner = user['user_hash']
			cur.execute(sql, [title, description, assigned_to, kanban_category, group_id, completed, owner, due_date, 0])
			db.commit()
			db.close()
			success.append("Successfully Added a Card")

	return render_template('kanban_add_card.html', user=user, members=members, category=category, errors=errors, success=success)



@app.route('/admin_create_user', methods=['POST', 'GET'])
def admin_create_user():
	user = session['user_hash']
	user = currentUser(user)
	errors = []
	success = []
	permissions = getAllPermissions()
	positions = getAllPositions()
	form_dict = {}
	if request.method == 'POST':
		form_dict = loadForm(form_dict)
		email = form_dict['email']
		permission = form_dict['permission']
		position = form_dict['position']
		user_hash = generate_password_hash(str(email) + str(permission) + str(position))
		sql = "INSERT INTO users (email, permission_id, position_id, user_hash, verified, organization) VALUES (%s, %s, %s, %s, %s, %s)"
		data = [email, permission, position, user_hash, 0, user['organization']]
		db, cursor = connect()
		cursor.execute(sql, data)
		db.commit()
		db.close()
		registration = "<p>You Have been Invited to Sign up at TaskKonnect.</p><br>"
		registration += "<p><a href='"+str(site_url)+"complete_signup/"+str(user_hash)+"'>Create Your Account</a></p>"
		msg = Message(subject='TaskKonnect Invite - CSC 394', html=registration, sender="webappforcsc394@gmail.com", recipients=[str(email)])
		mail.send(msg)
		success.append("A Signup Email has been sent to: " + str(email))
	if user and user['permission'] == 'administrator':
		return render_template('admin_create_user.html', user=user, errors=errors, success=success, permissions=permissions, positions=positions)
	else:
		return redirect(url_for('login'))

@app.route('/complete_signup/<user_hash>', methods=['POST', 'GET'])
def complete_signup(user_hash):
	errors = []
	success = []
	user = currentUser(user_hash)
	form_dict = {}
	if request.method == 'POST':
		form_dict = loadForm(form_dict)
		email = form_dict['email']
		first_name = form_dict['first_name']
		last_name = form_dict['last_name']
		password = generate_password_hash(form_dict['password'])
		confirm_password = form_dict['confirm_password']
		new_user_hash = generate_password_hash(str(email) + str(first_name) + str(last_name) + str(password))
		# Validate As Needed
		if form_dict['password'] != confirm_password:
			errors.append("Passwords do not Match.")
		if len(errors) == 0:
			db, cur = connect()
			sql = """
					UPDATE users 
					SET 
						first_name = %s, 
						last_name = %s, 
						password = %s, 
						user_hash = %s,
						verified = 1
					WHERE user_hash = %s
				  """
			data = [first_name, last_name, password, new_user_hash, user_hash]
			cur.execute(sql, data)
			db.commit()
			db.close()

			session['user_hash'] = new_user_hash
			return redirect(url_for('home'))
			
	return render_template('register.html', current_data=user, errors=errors, success=success)

@app.route('/admin_manage_users', methods=['POST', 'GET'])
def admin_manage_users():
	user = session['user_hash']
	user = currentUser(user)
	db, cur = connect()
	sql = """
			SELECT * FROM users
		  """
	cur.execute(sql)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	users = []
	for row in results:
		d = {}
		for key,value in zip(columns, list(row)):
			d[key] = value
		users.append(d)

	return render_template('admin_manage_users.html', user=user, users=users, columns=columns)

@app.route('/admin_edit_user/<user_hash>', methods=['POST', 'GET'])
def admin_edit_user(user_hash):
	errors = []
	success = []
	user = session['user_hash']
	user = currentUser(user)
	permissions = getAllPermissions()
	positions = getAllPositions()
	db, cur = connect()
	sql = """
			SELECT 
				U.email as email, 
				U.first_name as first_name, 
				U.last_name as last_name,
				P.permission_name as permission_name,
				P.id as permission_id,
				POS.id as position_id,
				POS.position_name as position_name
			FROM users U
			JOIN permissions P
				ON P.id = U.permission_id
			JOIN positions POS
				ON POS.id = U.position_id
			WHERE U.user_hash = %s
		  """
	cur.execute(sql, [user_hash])
	result = cur.fetchone()
	columns = getColumns(cur)
	user_data = {}
	for key, value in zip(columns, list(result)):
		user_data[key] = value

	form_dict = {}

	if request.method == 'POST':
		form_dict = loadForm(form_dict)
		email = form_dict['email']
		first_name = form_dict['first_name']
		last_name = form_dict['last_name']
		permission_id = int(form_dict['permission_id'])
		position_id = int(form_dict['position_id'])

		sql = """
				UPDATE users
				SET
					email = %s,
					first_name = %s,
					last_name = %s,
					permission_id = %s,
					position_id = %s
				WHERE user_hash = %s
			  """
		data = [email, first_name, last_name, permission_id, position_id, user_hash]
		cur.execute(sql, data)
		db.commit()
		db.close()

		user_data = form_dict
		user_data['permission_id'] = int(user_data['permission_id'])
		user_data['position_id'] = int(user_data['position_id'])
		
		success.append("Updated User's Info")

	return render_template('admin_edit_user.html', user_data=user_data, user=user, permissions=permissions, positions=positions, errors=errors, success=success)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

if __name__ == "__main__":
	app.run(debug=True)
