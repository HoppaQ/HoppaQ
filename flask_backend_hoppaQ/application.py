# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
import pandas as pd
from flask import send_file
__author__ = 'Utsav'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
import random
import mysql.connector 
# from DatabaseConnection import *

# mydb = get_connection()



# def get_connection():
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="1234",
	database="hoppaq_database"
)
	# return mydb
mycursor = mydb.cursor()

def get_all_products():

	mycursor.execute("select * from product, brand where product.idbrand = brand.idbrand")
	brands = mycursor.fetchall()

	mycursor.execute(" select product.nameproduct, product_description.description, product_description.manufacture_date, product_description.expiration_date  from product, product_description where product.idproduct = product_description.idproduct")
	description = mycursor.fetchall()

	mycursor.execute("select product.nameproduct, product_price.priceproduct from  product, product_price where product.idproduct = product_price.idproduct")
	price = mycursor.fetchall()

	mycursor.execute("select product.nameproduct, product_weights.weightproduct from  product, product_weights where product.idproduct = product_weights.idproduct")
	weight = mycursor.fetchall()

	print(brands)
	print(description)
	print(price)
	print(weight)


get_all_products()

brandToPk = {'tasty':4, 'know':2, 'fevikwik':3}
#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

productList = []


def randomNumberGenerator():
	"""
	Generate a random number every 1 second and emit to a socketio instance (broadcast)
	Ideally to be run in a separate thread?
	"""
	#infinite loop of magical random numbers
	print("Making random numbers")
	while not thread_stop_event.isSet():
		with open("../records.csv", "r+") as f:

			text = f.read()
			f.truncate(0)
			f.close()
		listX = text.split(",")
		try:
			name = listX[0]
			brandName = listX[1]
			qty = listX[2]
			price = listX[3]
			status = listX[4]
			data = {'name': name, 'brandName':brandName ,'qty':qty, 'price':price, 'status':status}
			socketio.emit('newnumber', data, namespace='/test')
			productList.append(data)
			socketio.sleep(2)
		except:
			socketio.sleep(2)


@app.route('/')
def index():
	#only by sending this page first will the client be connected to the socketio instance
	return render_template('cart.html')

@socketio.on('connect', namespace='/test')
def test_connect():
	# need visibility of the global thread object
	global thread
	print('Client connected')

	#Start the random number generator thread only if the thread has not been started before.
	if not thread.isAlive():
		print("Starting Thread")
		thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
	print('Client disconnected')

@app.route('/<idX>', methods=['GET','POST'])
def onProductClick(idX):
	# print(idX)
	# global currentProductId 
	# currentProductId= idX
	mycursor.execute(f'''select * FROM item WHERE (idinvoice = "{idX}")''')
	invoice = mycursor.fetchall()
	# df = []
	# for i in invoice:
	# 	dictB = {}
	# 	dictB['Product'] = i[0]
	# 	dictB['Date'] = i[2]
	# 	dictB['Amount'] = i[3]
	# 	df.append(dictB)

	# return (render_template('/purchase_history.html',data=df))

	# '''Invoice, Name, Date, Amount (bill)'''
	# df=query_db(q)
	# valMaxBid = getMaxBid()
	# if valMaxBid ==0:
	#     valMaxBid = "No Bid Yet"
	# global currentProductUserID
	# print(type(df['OWNER_ID']))
	# print(len(df['OWNER_ID']))
	# print(df['OWNER_ID'])
	# currentProductUserID = df['OWNER_ID']
	# df['maxBid'] = valMaxBid
	# print(currentProductUserID)
	# print(df)
	# for i in df:
	#    print(df[i])
	return (render_template('/single-product.html',data=invoice))

@app.route('/history', methods=['GET','POST'])
def history():
	'''Invoice, Name, Date, Amount
	Above is the object that should be queried and be sent in the df for frontend to render'''


	# q=str(f'''SELECT * FROM Project WHERE (PROJECT_ID = "{idX}")''')
	mycursor.execute(f'''select * FROM invoice WHERE (iduser = 1)''')
	invoice = mycursor.fetchall()
	# df =[]
	# for i in invoice:
	# 	dictB = {}
	# 	dictB['Invoice'] = i[0]
	# 	dictB['User'] = i[1]
	# 	dictB['Date'] = i[2]
	# 	dictB['Amount'] = i[3]
	# 	df.append(dictB)
	# df = pd.dataframe(df)
	# print(df)
	return (render_template('/purchase_history.html',data=invoice))


@app.route('/invoice', methods=['GET','POST'])
def Invoice():
	'''Invoice, Name, Date, Amount
	Above is the object that should be queried and be sent in the df for frontend to render'''

	invID = random.randint(10000,99999)
	# q=str(f'''SELECT * FROM Project WHERE (PROJECT_ID = "{idX}")''')
	mycursor.execute(f"insert into invoice values ({invID},1,2012-05-14,130)" )
	for i in range(len(productList)):
		mycursor.execute(f"insert into item values (1,{invID},{brandToPk[productList[i]['brandName']]},1,2012-05-14)")
	path = "inv-001.pdf"
	return send_file(path, as_attachment=True)


if __name__ == '__main__':
	socketio.run(app)
