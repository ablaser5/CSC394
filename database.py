import pymysql


def connect():
	# Open database connection
	db = pymysql.connect("localhost","root","Qpalzm11@","csc394" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	return db, cursor