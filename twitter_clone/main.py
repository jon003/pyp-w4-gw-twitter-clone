import sqlite3
from hashlib import md5
from functools import wraps
from flask import Flask
from flask import (g, request, session, redirect, render_template,
                   flash, url_for)

app = Flask(__name__)


def connect_db(db_name):
    return sqlite3.connect(db_name)


@app.before_request
def before_request():
    g.db = connect_db(app.config['DATABASE'][1])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# implement your views here

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'



        
# Check if user exists and hashed pass matches, if it does then set session
# if not, then tell them user or pass does not exists. (tests line 73)
@app.route('/login', methods=['GET', 'POST'])
def login(): # jon
    # Need this to pass test on line 57.
    if 'username' in session:
          return redirect(url_for('index'))
          
    if request.method == 'POST':
        # extract from the form.
        plaintext = request.form['password']
        username = request.form['username']
        # turn plaintext pass into md5 hash
        md5text = md5(plaintext).hexdigest() 
        # Sanitize SQL, then extract a single user object from DB.
        userlist = g.db.execute('SELECT id, username, password FROM user where username = ?', (username,))
        # fetchone to pop the first instance matching above query.
        user = userlist.fetchone()
        if user and user[2] == md5text:
            userid = user[0]
            session['username'] = username
            session['user_id'] = userid
            return redirect(url_for('index')) # redirect them to the next page.
    flash('Invalid username or password')
    return render_template('login.html')

# this should not be needed. need to figure out why.
#username = ''

@app.route('/')
@login_required
def index(): # jon
    # I have to be invoked after login.
    if 'username' in session:
        # redirect them to the next page.
        return redirect('/{}'.format(session['username']))


# just a post, deletes session.
@app.route('/logout', methods=['POST'])
def logout(): # jon
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])  # prashant will try.
@login_required
def profile():
    #shows username, location, etc
    pass


@app.route('/<username>', methods=['GET', 'POST']) # lana will try.
@login_required
# Test case list:
# - Feed not authenticated - read only
# - Feed authenticated - get
# - Feed authenticated - get other users feed
# - Feed authenticated - post
# - Feed not authenticated - post
def show_user_tweets():
    
    
    
    pass