import mysql.connector


def get_connection():
	mydb = mysql.connector.connect(
	  host="localhost",
	  user="root",
	  password="1234",
	  database="hoppaq_database"
	)
	return mydb

