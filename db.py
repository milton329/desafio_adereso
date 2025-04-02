from peewee import MySQLDatabase
from config import DATABASE_PARAMS

db = MySQLDatabase(None)

def initialize_database(app):
    db.init(**DATABASE_PARAMS)
    app.before_request(open_database)
    app.teardown_request(close_database)

def open_database():
    db.connect()

def close_database(response_or_exc):
    if not db.is_closed():
        db.close()