from flask import Flask
from flask_socketio import SocketIO
import os, sqlite3
import socket as sock

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.debug = True

socketio = SocketIO(app, async_mode='gevent')

# Database setup
conn = sqlite3.connect('speedskate.db')
db = conn.cursor()
db.execute('CREATE TABLE IF NOT EXISTS skates (id TEXT, time TEXT, size REAL, age TINYINT, type TINYINT, state TINYINT)')
conn.commit()

# Prompt for password on run
password = input('Queue password: ')
_ = os.system('cls' if os.name == 'nt' else 'clear')
print('SpeedSkate Version 1.0')

queue = {}

# Print system IP address
s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))    # Google DNS
print('IP address: {}'.format((s.getsockname()[0])))
s.close()
print('========================================================================')

from app import views, socket
