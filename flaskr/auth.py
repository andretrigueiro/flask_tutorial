'''
Study reviews - André Trigueiro:

This file refers to the authentication functions, also called blueprint.
It is a way to organize a group of related views and other code.

#@bp.route associates the URL /register with the register view function.
#If the user submitted the form, request.method will be 'POST'. In this case, start validating the input.
#request.form is a special type of dict mapping submitted form keys and values.
#If validation succeeds, insert the new user data into the database.
#db.execute takes a SQL query with ? placeholders for any user input, and a tuple of values to replace the placeholders with.
#For security, passwords should never be stored in the database directly. Instead, generate_password_hash() is used to securely hash the password, and that hash is stored.
 Since this query modifies data, db.commit() needs to be called afterwards to save the changes.
#An sqlite3.IntegrityError will occur if the username already exists, which should be shown to the user as another validation error.
#fetchone() returns one row from the query. If the query returned no results, it returns None. Later, fetchall() will be used, which returns a list of all results.
#check_password_hash() hashes the submitted password in the same way as the stored hash and securely compares them.
#session is a dict that stores data across requests. When validation succeeds, the users id is stored in a new session. 
 The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests. 
 Flask securely signs the data so that it cant be tampered with.
# load_logged_in_user checks if a user id is stored in the session and gets that users data from the database, storing it on g.user.

'''

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#Register view, code to return a HTML after the user visits the /auth/register URL
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

#Login view
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    
    else:
        return render_template('auth/login.html')

    return render_template('auth/login.html')

#Function that runs before the view function, no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

#Function to remove the user id from the session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#Function to checks if a user is loaded and redirects to the login page otherwise. 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view