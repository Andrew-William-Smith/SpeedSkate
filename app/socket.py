from flask import request, session
from flask_socketio import emit
import uuid

from app import app, conn, db, socketio, queue

@socketio.on('connect')
def connected():
  if 'authorised' not in session or not session['authorised']:
    emit('denyRequest', room=request.sid)
    return

  overrideQueue = []
  for key, val in queue.items():
    overrideQueue.append(dict({'id': key}, **val))

  emit('overrideQueue', overrideQueue, room=request.sid)

@socketio.on('addRequest')
def addRequest(data):
  if 'authorised' not in session or not session['authorised']:
    emit('denyRequest', room=request.sid)
    return

  # Add skate information to database
  id = str(uuid.uuid4())
  skateInfo = (id,
               data['time'],
               float(data['size']),
               (1 if data['age'] == 'youth' else 0),
               ('figure', 'hockey', 'speed').index(data['type']),
               0)
  db.execute("INSERT INTO skates VALUES(?, ?, ?, ?, ?, ?)", skateInfo)
  conn.commit()

  # Add skate information to memory queue
  queueItem = {'time':   data['time'],
               'size':   float(data['size']),
               'age':    data['age'],
               'type':   data['type'],
               'status': 0}
  queue[id] = queueItem

  print('+ {}: Size {}{} {}'.format(id, data['size'], ('Y' if data['age'] == 'youth' else ''), data['type']))

  # Acknowledge addition
  emit('addSuccess', id, room=request.sid)
  emit('pubRequest', dict({'id': id}, **queueItem), broadcast=True)

@socketio.on('cancelRequest')
def cancelRequest(id):
  if 'authorised' not in session or not session['authorised']:
    emit('denyRequest', room=request.sid)
    return

  if id in queue:
    queue.pop(id, None)
    db.execute("DELETE FROM skates WHERE id = ?", (id,))
    conn.commit()
    print('- ' + id)
    emit('deleteRequest', id, broadcast=True)

@socketio.on('changeState')
def changeState(data):
  if 'authorised' not in session or not session['authorised']:
    emit('denyRequest', room=request.sid)
    return

  id = data['id']
  if id in queue:
    state = int(data['state'])
    db.execute("UPDATE skates SET state = ? WHERE id = ?", (state, id))
    conn.commit()
    queue[id]['status'] = state

    emit('pubState', {'id': id, 'state': state}, broadcast=True)
