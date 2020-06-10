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
def addUser(gid, user_hash):
	db,cur = connect()
	sql = "INSERT INTO user_groups (g_id,user) VALUES (%s,%s)"
	data = [gid,user_hash]
	cur.execute(sql,data)
	db.commit()
	db.close()

def getUserGroups(user_hash):
	db,cur = connect()
	sql = "SELECT *  FROM user_groups UG JOIN groups G ON G.g_id = UG.g_id WHERE UG.user = %s"
	cur.execute(sql,user_hash)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	gid = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		gid.append(r)
	return gid

def getCardsByGroup(group_id):
	db,cur = connect()
	sql = """
			SELECT *  
			FROM cards C
			WHERE C.group_id = %s 
		  """
	cur.execute(sql, [group_id])
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	cards = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		cards.append(r)
	return cards

def getKanbanCards(group_id, category):
	db,cur = connect()
	sql = """
			SELECT 
				*,
				C.id as card_id 
			FROM cards C
			JOIN users U
				ON U.user_hash = C.assigned_to
			WHERE C.group_id = %s AND C.kanban_category = %s
		  """
	cur.execute(sql,[group_id, category])
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	cards = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		cards.append(r)
	return cards

def getKanbanCard(card_id):
	db,cur = connect()
	sql = """
			SELECT 
				*,
				C.id as card_id 
			FROM cards C
			JOIN users U
				ON U.user_hash = C.assigned_to
			WHERE C.id = %s
		  """
	cur.execute(sql,[card_id])
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		return r
	return None

def getKanbanCardComments(card_id):
	db,cur = connect()
	sql = """
			SELECT 
				CC.*,
				U.first_name
			FROM card_comments CC
			JOIN users U
				ON U.user_hash = CC.user
			WHERE card_id = %s
		  """
	cur.execute(sql,[card_id])
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	c = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		c.append(r)
	return c

def moveKanbanCard(card_id, destination):
	db,cur = connect()
	sql = """
			UPDATE
				cards
			SET
				kanban_category = %s
			WHERE id = %s
		  """
	cur.execute(sql, [destination, card_id])
	db.commit()
	db.close()

def getGroupMembers(group_id):
	db,cur = connect()
	sql = """
			SELECT *
			FROM user_groups UG
			JOIN users U
				ON U.user_hash = UG.user
			WHERE UG.g_id = %s
		  """
	cur.execute(sql, group_id)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	members = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		members.append(r)
	return members

def deleteUser(gid,user_hash):
	db,cur = connect()
	sql = "DELETE  FROM user_groups WHERE user = %s"
	data = [user_hash]
	cur.execute(sql,data)
	db.commit()
	db.close()

def getCurrentUser(user_hash, email = None):
	db,cur = connect()
	sql = """
			SELECT
				U.email as email,
				U.first_name as first_name,
				U.last_name as last_name,
				P.permission_name as permission,
				U.user_hash as user_hash,
				U.verified as verified,
				U.organization as organization
			FROM users U
			JOIN permissions P
				ON P.id = U.permission_id
		  """
	if email:
		sql += "WHERE email = %s"
		cur.execute(sql, [email])
	else:
		sql += "WHERE user_hash = %s"
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
	db.close()
	if result:
		return True
	else:
		return False

def isUnverified(email):
	db, cur = connect()
	sql = "SELECT verified FROM users WHERE email = %s"
	cur.execute(sql, [email])
	result = cur.fetchone()
	db.close()
	if result:
		if result[0] == 1:
			return False
		if result[0] == 0:
			return True
	return True

def getUserPermission(user_hash):
	db, cur = connect()
	sql = """
			SELECT 
				P.permission_name
			FROM users U
			JOIN permissions P
				ON P.id = U.permission_id
			WHERE U.user_hash = %s
		  """
	cur.execute(sql, [user_hash])
	result = cur.fetchone()
	db.close()
	if result:
		return result[0]
	else:
		return None

def currentUser(user_hash):
	user = getCurrentUser(user_hash)
	if user:
		return user
	else:
		return None
def getAllUsers():
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
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		users.append(r)
	return users
def getAllPermissions():
	db, cur = connect()
	sql = """
			SELECT * FROM permissions
		  """
	cur.execute(sql)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	permissions = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		permissions.append(r)
	return permissions

def getAllGroups(user_hash):
	db, cur = connect()
	sql = """
			SELECT * FROM groups WHERE owner = %s;
		  """
	cur.execute(sql, user_hash)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	groups = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		groups.append(r)
	return groups

def getUserHash(id):
	db, cur = connect()
	sql = """
			SELECT user_hash FROM users where id = %s
		  """
	cur.execute(sql, id)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	userHash = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		userHash.append(r)
	return userHash

def getUsersByGroups(gid):
	db, cur = connect()
	sql = """
			SELECT first_name, last_name, g_id, id FROM users  inner join user_groups on
 			user_groups.user = users.user_hash 
			where g_id = 
		  """ 
	sql += gid
	cur.execute(sql)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	names = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		names.append(r)
	return names

def getAllPositions():
	db, cur = connect()
	sql = """
			SELECT * FROM positions
		  """
	cur.execute(sql)
	results = cur.fetchall()
	columns = getColumns(cur)
	db.close()
	positions = []
	for row in results:
		r = {}
		for col,val in zip(columns, list(row)):
			r[col] = val
		positions.append(r)
	return positions

def getSiteURL():
	db, cur = connect()
	sql = """
			SELECT site_url FROM config
		  """
	cur.execute(sql)
	result = cur.fetchone()
	return result[0]


