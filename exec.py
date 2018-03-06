#!speedskate/bin/python
from app import app, socketio

socketio.run(app, '0.0.0.0', 5000, debug=True, use_reloader=False)
