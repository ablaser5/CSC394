from flask import Flask, render_template, request
from database import connect

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
	email = None
	password = None

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		first_name = 'Aaron'
		last_name = 'Blaser'
		perm = 1
		position_id = 1

		error = 0
		if not (email and not (email == '' or email == ' ')):
			error += 1
		if not (password and not (password == '' or password == ' ')):
			error += 1

		if error == 0:
			sql = "INSERT INTO users (email, first_name, last_name, password, permission_id, position_id) VALUES (%s, %s, %s, %s, %s, %s)"
			data = [email, first_name, last_name, password, perm, position_id]
			db, cursor = connect()

			cursor.execute(sql, data)
			db.commit()
			db.close()
		else:
			print("There Was an Error.")


	return render_template('index.html', email=email, password=password)

if __name__ == "__main__":
	app.run(debug=True)
