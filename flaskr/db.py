import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            # Use the configuration from the running app's 'DATABASE'
            current_app.config['DATABASE'],
            # Enables parsing of certain SQLite column types (e.g., DATE and DATETIME) 
            #to Python types (e.g., datetime.date and datetime.datetime).
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    # Create the db through get_db()
    db = get_db()
    # f = return value of current_app.open_resource('schema.sql')
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Define a command line command called init-db
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# sqlite3.register_converter(typename, converter, /)
# convert SQLite objects of type typename into a Python object of a specific type
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    # app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)
