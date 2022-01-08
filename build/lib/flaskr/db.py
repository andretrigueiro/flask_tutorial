'''
Study reviews - André Trigueiro:

This file refers to the database configuration.
It creates a connection with a SQLite database. Any queries and operations are performed using the connection, which is closed after the work is finished.
In web applications this connection is typically tied to the request. It is created at some point when handling a request, and closed before the response is sent.

#g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. 
 The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
#current_app is another special object that points to the Flask application handling the request. 
 Since you used an application factory, there is no application object when writing the rest of your code. 
 get_db will be called when the application has been created and is handling a request, so current_app can be used.
#sqlite3.connect() establishes a connection to the file pointed at by the DATABASE configuration key.
#sqlite3.Row tells the connection to return rows that behave like dicts.
#close_db checks if a connection was created by checking if g.db was set. If the connection exists, it is closed.
#open_resource() opens a file relative to the flaskr package
#click.command() defines a command line command called init-db that calls the init_db function and shows a success message to the user. 
#app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.
#app.cli.add_command() adds a new command that can be called with the flask command.

'''

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

#Function to connect with Database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

#Function to close the Database
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

#Function to create the Database
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#New command with terminal
@click.command('init-db')
@with_appcontext

#Function to initiate the Database and shows it to the user
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

#Function to take an application and does the registration to close_db and init_db_command can work
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)