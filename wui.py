# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~
    A microblog example application written as Flask tutorial with
    Flask and sqlite3.
    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import config

# create our little application :)
from db import DB, MySQLCursor, MongoDBConnection

app = Flask(__name__)

# Load default config and override config from an environment variable
config_dict = {k: getattr(config, k) for k in dir(config) if not k.startswith('_')}
app.config.update(config_dict)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
))


def get_mysql_db():
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = DB.mysql_connection()
    return g.mysql_db


def get_mongo_db():
    if not hasattr(g, 'mongo_db'):
        g.mongo_db = DB.mongodb_connection()
    return g.mongo_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()
    if hasattr(g, 'mongo_db'):
        g.mongo_db.close()


@app.route('/')
def index():
    return render_template('index.html', title='An-Empirical-Study-of-News-RSS-Feeds')


@app.route('/mysql/users')
def mysql_users():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 100))
    with MySQLCursor() as cursor:
        cursor.execute('select id, uname from userdata limit %(start)s, %(limit)s',
                       {'start': start, 'limit': limit})
        columns = [d[0] for d in cursor.description]
        entries = cursor.fetchall()
        cursor.execute('select count(*) from userdata')
        count,  = cursor.fetchone()
    return render_template('mysql_data.html', title=u'Users', columns=columns, entries=entries, count=count)


@app.route('/mysql/news/')
def mysql_news():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 100))
    with MySQLCursor() as cursor:
        cursor.execute('select * from newsdata limit %(start)s, %(limit)s',
                       {'start': start, 'limit': limit})
        columns = [d[0] for d in cursor.description]
        entries = cursor.fetchall()
        cursor.execute('select count(*) from newsdata')
        count, = cursor.fetchone()
    return render_template('mysql_data.html', title=u'Mysql News', columns=columns, entries=entries, count=count)


@app.route('/mysql/user_news')
def mysql_user_news():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 100))
    with MySQLCursor() as cursor:
        cursor.execute('select * from user_read_news limit %(start)s, %(limit)s',
                       {'start': start, 'limit': limit})
        columns = [d[0] for d in cursor.description]
        entries = cursor.fetchall()
        cursor.execute('select count(*) from newsdata')
        count, = cursor.fetchone()
    return render_template('mysql_data.html', title=u'Mysql User News', columns=columns, entries=entries, count=count)


@app.route('/mongodb/users')
def mongodb_users():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 100))
    with MongoDBConnection() as db:
        entries = db.userdata.find()[start:start+limit]
        count = db.userdata.count()
    return render_template('mongo_data.html', title=u'MongoDB Users', entries=entries, count=count)

@app.route('/mongodb/news')
def mongodb_news():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 100))
    with MongoDBConnection() as db:
        entries = db.newsdata.find()[start:start+limit]
        count = db.newsdata.count()
    return render_template('mongo_data.html', title=u'MongoDB News', entries=entries, count=count)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == "__main__":
    app.run(debug=True)