from flask import redirect, render_template, request, session
from app import app, password

@app.route('/')
def index():
  if 'authorised' in session and session['authorised']:
    return render_template('main.html', mode=session['mode'])
  else:
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    request.get_data()
    if request.form['password'] == password:
      session['authorised'] = True
      session['mode'] = 'registrar' if 'registrar' in request.form else 'fulfiller'
      return redirect('/')
    else:
      return render_template('login.html', incorrect='incorrect')

  else:
    if 'authorised' in session and session['authorised']:
      return redirect('/')
    else:
      return render_template('login.html')

@app.route('/logout')
def logout():
  session['authorised'] = False
  return redirect('/login')
