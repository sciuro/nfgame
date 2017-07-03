# all the imports
import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, abort, \
     render_template, flash, session
import random
from datetime import datetime, timedelta

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
    START_KEY = 'None',
    MAX_TIME = '3600',
    SHOW_TIME = '120',
    REFRESH_TIME = '10',
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
    """Calculate starttime"""
    now = datetime.now() - timedelta(seconds=int(app.config['MAX_TIME'])) - timedelta(seconds=int(app.config['SHOW_TIME']))
    maxstarttime = datetime.strptime((str(now.year)+"-"+str(now.month)+"-"+str(now.day)+" "+str(now.hour)+":"+str(now.minute)+":"+str(now.second)), "%Y-%m-%d %H:%M:%S")

    db = get_db()
    cur = db.execute('select * from score where starttime > ? order by duration asc', [maxstarttime])
    entries = cur.fetchall()

    user = {}
    tags = app.config['TAGS']
    timeremaining = {}

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

        '''Calculate time remaining'''
        starttime = datetime.strptime(entry['starttime'], "%Y-%m-%d %H:%M:%S")
        endtime = starttime + timedelta(seconds=int(app.config['MAX_TIME']))
        playtime = endtime - datetime.now()
        if datetime.now() > endtime:
            timeremaining[entry['id']] = "Time's up"
        else:
            hours = playtime.seconds / 3600
            minutes = (playtime.seconds - (hours * 3600)) / 60
            seconds = playtime.seconds - (minutes * 60)
            if len(str(minutes)) == 1:
                minutes = '0' + str(minutes)
            if len(str(seconds)) == 1:
                seconds = '0' + str(seconds)
            timeremaining[entry['id']] = str(hours) + ":" + str(minutes) + ":" + str(seconds)

    return render_template('overview.html', entries=entries, tags=app.config['TAGS'], user=user, type='Current players', refresh=app.config['REFRESH_TIME'], timeremaining=timeremaining)

@app.route('/highscores')
def highscores():
    tagquery = ""
    for tag in app.config['TAGS']:
        if tagquery == "":
            tagquery = 'where tags like "%' + tag + '%"'
        else:
            tagquery = tagquery + ' and tags like "%' + tag + '%"'

    db = get_db()
    cur = db.execute('select * from score ' + tagquery + ' order by duration asc')
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

    return render_template('highscores.html', entries=entries, tags=app.config['TAGS'], user=user, type='Highscores', refresh=app.config['REFRESH_TIME'])

@app.route('/newuser/', methods=['GET', 'POST'])
@app.route('/newuser/<string:newhash>/', methods=['GET', 'POST'])
def new_user(newhash='None'):
    """Check if there is a key to the new user"""
    if not app.config['START_KEY'] == 'None':
        if not newhash == app.config['START_KEY']:
            return redirect(url_for('index'))

    """If it's a GET request, no new user should be made"""
    if request.method == 'GET':
      return render_template('newuser.html', newhash=newhash)

    """Now we got a POST request"""

    now = datetime.now()
    time = datetime.strptime((str(now.year)+"-"+str(now.month)+"-"+str(now.day)+" "+str(now.hour)+":"+str(now.minute)+":"+str(now.second)), "%Y-%m-%d %H:%M:%S")

    """Check for unique username"""
    db = get_db()
    cur = db.execute('select count(username) as count from score where username = ? COLLATE NOCASE', [request.form['username']])
    usercount = cur.fetchone()

    if not usercount['count'] == 0:
        return render_template('newuser.html', newhash=newhash, msg='Username already taken!')

    db = get_db()
    cur = db.execute("insert into score (username,starttime,duration) values (?, ?, ?)", [request.form['username'], time, '99:99:99'])
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
        '''If a user does not require central registration show new user form'''
        if app.config['START_KEY'] == 'None':
            session['tag'] = taghash
            return redirect(url_for('new_user'))
        else:
            return render_template('gotoregistration.html', registration=app.config['REGISTRATION_DESK'], color='#FF9999')

    tags = app.config['TAGS']

    if not tags.has_key(taghash):
        return render_template('tagnotfound.html', color='#FF9999')

    db = get_db()
    cur = db.execute('select * from score where id = ?', [session['id']])
    entries = cur.fetchall()
    
    if not entries:
        session['tag'] = taghash
        return redirect(url_for('new_user'))

    '''Calculate duration'''
    starttime = datetime.strptime(entries[0]['starttime'], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    lasttime = datetime.strptime((str(now.year)+"-"+str(now.month)+"-"+str(now.day)+" "+str(now.hour)+":"+str(now.minute)+":"+str(now.second)), "%Y-%m-%d %H:%M:%S")

    timediff = lasttime - starttime
    hours = timediff.seconds / 3600
    minutes = (timediff.seconds - (hours * 3600)) / 60
    seconds = timediff.seconds - (minutes * 60)
    if len(str(minutes)) == 1:
        minutes = '0' + str(minutes)
    if len(str(seconds)) == 1:
        seconds = '0' + str(seconds)
    time = str(hours) + ":" + str(minutes) + ":" + str(seconds)

    if int(timediff.seconds) > int(app.config['MAX_TIME']):
        return render_template('timeout.html', color='#FF9999')

    '''Calculate time remaining'''
    endtime = starttime + timedelta(seconds=int(app.config['MAX_TIME']))
    playtime = endtime - now
    hours = playtime.seconds / 3600
    minutes = (playtime.seconds - (hours * 3600)) / 60
    seconds = playtime.seconds - (minutes * 60)
    if len(str(minutes)) == 1:
        minutes = '0' + str(minutes)
    if len(str(seconds)) == 1:
        seconds = '0' + str(seconds)
    timeremaining = str(hours) + ":" + str(minutes) + ":" + str(seconds)

    cur_score = entries[0]['tags']
    if cur_score == None:
        cur_score = taghash
    else:
        found_tags = cur_score.split(',')
        for found_tag in found_tags:
            if taghash == found_tag:
                return render_template('tagalreadyfound.html', tagname=tags.get(taghash), color='#FFFF80', time=timeremaining)
                break

        cur_score = cur_score + "," + taghash

    db = get_db()
    cur = db.execute('update score set tags = ?, lasttime = datetime(), duration = ? where id = ?', [cur_score, time, session['id']])
    db.commit()

    return render_template('tagfound.html', tagname=tags.get(taghash), color='#00FF00', time=timeremaining)

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
    app.run(threaded=True)
