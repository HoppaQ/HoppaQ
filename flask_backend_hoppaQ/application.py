# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event

__author__ = 'Utsav'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.isSet():
        with open("./newfile.csv", "r+") as f:

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
            socketio.emit('newnumber', {'name': name, 'brandName':brandName ,'qty':qty, 'price':price, 'status':status}, namespace='/test')
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
    print(idX)
    global currentProductId 
    currentProductId= idX
    q=str(f'''SELECT * FROM Project WHERE (PROJECT_ID = "{idX}")''')
    '''Invoice, Name, Date, Amount (bill)'''
    df=query_db(q)
    valMaxBid = getMaxBid()
    if valMaxBid ==0:
        valMaxBid = "No Bid Yet"
    global currentProductUserID
    print(type(df['OWNER_ID']))
    print(len(df['OWNER_ID']))
    print(df['OWNER_ID'])
    # currentProductUserID = df['OWNER_ID']
    df['maxBid'] = valMaxBid
    # print(currentProductUserID)
    # print(df)
    # for i in df:
    #    print(df[i])
    return (render_template('/single-product.html',data=df))

@app.route('/history', methods=['GET','POST'])
def history():
    '''Invoice, Name, Date, Amount
    Above is the object that should be queried and be sent in the df for frontend to render'''


    q=str(f'''SELECT * FROM Project WHERE (PROJECT_ID = "{idX}")''')
    # '''Invoice, Name, Date, Amount (bill)'''
    df=query_db(q)
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
    return (render_template('/purchase_history.html',data=df))


if __name__ == '__main__':
    socketio.run(app)
