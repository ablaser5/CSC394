import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

# Connects to the database and returns the database object with the cursor
def connect():
	# Open database connection
	db = pymysql.connect("localhost","root","Qpalzm11@","csc394" ) # EDIT THIS TO FIT YOUR CONFIG
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	return db, cursor

def getColumns(cursor):
	columns = [item[0] for item in cursor.description]
	return columns

def getCurrentUser(user_hash, email = None):
	db,cur = connect()
	if email:
		sql = "SELECT * FROM users WHERE email = %s"
		cur.execute(sql, [email])
	else:
		sql = "SELECT * FROM users WHERE user_hash = %s"
		cur.execute(sql, [user_hash])
	results = cur.fetchall()
	cols = getColumns(cur)
	user_dict = {}
	for row in results:
		for key, value in zip(cols,list(row)):
			user_dict[key] = value
	db.close()
	return user_dict

# Verifies the user's email after signup
def verifyUser(user_hash):
	sql = """
			SELECT * FROM users WHERE user_hash = %s
		  """
	data = [user_hash]
	db, cur = connect()
	cur.execute(sql, data)
	result = cur.fetchone()
	if result:
		sql = "UPDATE users SET verified = 1 WHERE user_hash = %s"
		cur.execute(sql, data)
		db.commit()
		db.close()
		return True
	else:
		db.close()
		return False

# Checks an user's login credentials
def checkUser(email, password):
	db, cur = connect()
	sql = "SELECT email, password FROM users WHERE email = %s"
	data = [email]
	cur.execute(sql, data)
	result = cur.fetchone()
	db.close()
	if result:
		if check_password_hash(result[1], password):
			return True
		else:
			return False
	return False

def alreadyAnUser(email):
	db, cur = connect()
	sql = "SELECT email FROM users WHERE email = %s"
	cur.execute(sql, [email])
	result = cur.fetchone()
	if result:
		return True
	else:
		return False

def isUnverified(email):
	db, cur = connect()
	sql = "SELECT verified FROM users WHERE email = %s"
	cur.execute(sql, [email])
	result = cur.fetchone()
	if result:
		if result[0] == 1:
			return False
		if result[0] == 0:
			return True
	return True
