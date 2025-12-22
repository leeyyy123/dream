from flask import g
from sql.mysql import ConnectDB
from utils.status import Status

def get_db():
    """Get database connection, creating one if it doesn't exist"""
    if 'db' not in g:
        connection = ConnectDB()
        if isinstance(connection, Status):
            g.db = None
        else:
            g.db = connection
    return g.db

def close_db(e=None):
    """Close database connection if it exists"""
    db = g.pop('db', None)
    if db is not None and db.open:
        db.close()

def init_app(app):
    """Register database functions with app"""
    app.teardown_appcontext(close_db)