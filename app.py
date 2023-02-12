"""
Create a webpage that is constantly updated with random numbers from a background python process.
"""

# Start with a basic flask app webpage.
from tkinter.font import names
from turtle import forward
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
from random import randint
import serial,json
from model import limits, steering, movement
from socket import socket, AF_INET, SOCK_DGRAM
__author__ = 'Eremita'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False

#turn the flask app into a socketio app
socketio = SocketIO(app,async_mode = "threading",logging = False, engineio_logger = False)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

#serial comunication thread
s_thread = Thread()
serial_stop_event = Event()

count = 0

class RandomThread(Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        print("Making random numbers")
        while not thread_stop_event.isSet():
            number = randint(11111, 99999)
            #print(number)
            socketio.emit('newnumber', {'number': number}, namespace='/test')
            sleep(self.delay)

    def run(self):
        self.randomNumberGenerator()


@app.route('/')
def index():
    return render_template('dev.html')

@app.route('/admin')
def admin():
    return render_template('dev.html')

@app.route('/dev')
def dev():
    return render_template('dev.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')
    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
    serial_stop_event.set()

@socketio.on('stop')
def stop_connections():
    serial_stop_event.set()
    thread_stop_event.set()

@socketio.on('message', namespace='/test')
def received_msg(data):
    SERVER_IP   = "127.0.0.1"
    PORT_NUMBER = 4000
    SIZE = 1024
    mySocket = socket( AF_INET, SOCK_DGRAM )
    data_str = bytes(str(data).encode("utf-8"))
    mySocket.sendto(data_str,(SERVER_IP,PORT_NUMBER))



if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, log_output = False)
