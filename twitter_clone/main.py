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

'''
@app.after_request
def after_request():
    pass
    # do save/commit/close DB stuff here.
    # g.db = connect_db(app.config['DATABASE'][1])
'''

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
        userlist = g.db.execute('SELECT id, username, password FROM user WHERE username = ?', (username,))
        # fetchone to pop the first instance matching above query.
        user = userlist.fetchone()
        if user and user[2] == md5text:
            userid = user[0]
            session['username'] = username
            session['user_id'] = userid
            return redirect(url_for('index')) # redirect them to the next page.
    flash('Invalid username or password')
    return render_template('login.html')


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
@login_required  # unless we can view another users' profile.
def profile():
    user_id = session['user_id'] # we know this is set because @login_required
    
    if request.method == 'POST':
        # update the profile in the database
        # copied over profile.html from static, updated for these variables:
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        
        # sql command to update the database
        g.db.execute(
            'UPDATE user SET username = ?, first_name = ?, last_name = ?, birth_date = ? WHERE user_id = ?', 
            (username, firstname, lastname, birthdate, user_id)
        )
        
        
    # View the profile
    # fetch profile info from DB.  inverse of the update.
    userdata = g.db.execute('SELECT username, firstname, lastname, birthdate FROM user WHERE id = ?', (user_id,))
    # fetchone to pop the first instance matching above query.
    user = userlist.fetchone() # indexable object
    rendering_variables = [
            user[0], # username
            user[1], # first_name
            user[2], # last_name
            user[3]  # birthdate
    ]
    return render_template('profile.html', rendering_variables)


# just playing around here! - jon
def tweetdump(): # jon
    # test function to just grab the tweet database, so I can learn how to 
    # access stuff.
    #tweetdumper = g.db.execute('SELECT id, user_id, created, content FROM tweet WHERE username = ?', (username,))
    tweetdumper = g.db.execute('SELECT id, user_id, created, content FROM tweet')
    # fetchone to pop the first instance matching above query.
    for tweet in tweetdumper:
        print(tweet)

''' schema reminder
  id INTEGER PRIMARY KEY autoincrement,
  user_id INTEGER,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  content TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id),
'''



@app.route('/<username>', methods=['GET', 'POST']) # lana will try.
@login_required
# Test case list:
# - Feed not authenticated - read only
# - Feed authenticated - get
# - Feed authenticated - get other users feed
# - Feed authenticated - post
# - Feed not authenticated - post
def show_user_tweets(username):
    pass