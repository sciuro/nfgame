# all the imports
import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, abort, \
     render_template, flash, session
import random

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'nfgame.db'),
    TAGS = {'taghash1': 'tagname1',
            'taghash2': 'tagname2',
            'taghash3': 'tagname3',
            'taghash4': 'tagname4'
           },
    SECRET_KEY = 'Very secret key!',
    ADMIN_PASSWORD = 'changeme!'
))
app.config.from_envvar('NFGAME_SETTINGS', silent=True)
app.secret_key = app.config['SECRET_KEY']

def connect_db():
    """Connects to the database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select * from score order by username')
    entries = cur.fetchall()

    user = {}
    tags = app.config['TAGS']

    for entry in entries:
        if entry['tags'] == None:
            found_tags = []
        else:
            found_tags = entry['tags'].split(',')

        user[entry['id']] = {}
        for tag in tags:
            user[entry['id']][tag] = 'Not'
            for found_tag in found_tags:
                if found_tag == tag:
                    user[entry['id']][tag] = 'Found'

    return render_template('overview.html', entries=entries, tags=app.config['TAGS'], user=user)

@app.route('/newuser', methods=['GET', 'POST'])
def new_user():
    """If it's a GET request, no new user should be made"""
    if request.method == 'GET':
      return render_template('newuser.html')

    """Now we got a POST request"""
    db = get_db()
    cur = db.execute("insert into score (username) values (?)", [request.form['username']])
    db.commit()
    session['username'] = request.form['username']

    db = get_db()
    cur = db.execute('select * from score where username = ?', [session['username']])
    entries = cur.fetchall()
    session['id'] = entries[0]['id']

    if not 'tag' in session:
        return render_template('newuser_done.html')
    else:
        return redirect(url_for('tag_found', taghash=session['tag']))

@app.route('/tag/<string:taghash>')
def tag_found(taghash):
    session.pop('tag', None)
    
    if not 'id' in session:
        session['tag'] = taghash
        return redirect(url_for('new_user'))

    tags = app.config['TAGS']

    if not tags.has_key(taghash):
        return render_template('tagnotfound.html', color='#FF9999')

    db = get_db()
    cur = db.execute('select * from score where id = ?', [session['id']])
    entries = cur.fetchall()
    
    if not entries:
        session['tag'] = taghash
        return redirect(url_for('new_user'))

    cur_score = entries[0]['tags']
    if cur_score == None:
        cur_score = taghash
    else:
        found_tags = cur_score.split(',')
        for found_tag in found_tags:
            if taghash == found_tag:
                return render_template('tagalreadyfound.html', tagname=tags.get(taghash), color='#FFFF80')
                break

        cur_score = cur_score + "," + taghash

    db = get_db()
    cur = db.execute('update score set tags = ? where id = ?', [cur_score, session['id']])
    db.commit()

    return render_template('tagfound.html', tagname=tags.get(taghash), color='#00FF00')

@app.route('/admin/<string:password>')
def admin_page(password):
    if password == app.config['ADMIN_PASSWORD']:
        return render_template('admin_page.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/deletescore')
def delete_score():
    db = get_db()
    cur = db.execute("delete from score")
    db.commit()
    
    return render_template('admin_page.html')

@app.route('/deleteuser')
def delete_user():
    session.pop('username', None)
    session.pop('id', None)

    return render_template('admin_page.html')

if __name__ == '__main__':
    app.run()
