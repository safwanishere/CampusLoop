import os
import sqlite3
from functools import wraps
from flask import session, redirect



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function


BASE_DIR = os.path.abspath(os.path.dirname("database.db"))

def dbConnection():
    connection = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))
    return connection