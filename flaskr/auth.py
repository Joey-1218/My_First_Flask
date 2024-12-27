import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# A blueprint named "auth", defined in current Python module
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Get the value entered in the username field
        username = request.form['username']
        # Get the value entered in the password field
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # execute(sql, parameters=(), /)
                # Create a new Cursor object and call execute() on it with the given sql and parameters.
                # Return the new cursor object.
                # This insert a pair of username and password into the database
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # This ensures that the changes are saved to the database file.
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # redirect() generates a redirect response to the generated URL.
                # url_for() generates the URL for the login view based on its name.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Get the value entered in the username field
        username = request.form['username']
        # Get the value entered in the password field
        password = request.form['password']
        db = get_db()
        error = None

        # this will search the username in database and return a line
        user = db.execute(
            'SELECT * FROM use WHERE username = ?', (username,)
        ).fetchone()

        # cannot find the username in the database
        if user is None:
            error = 'Incorrect username.'
        # password not match
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view