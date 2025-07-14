import os
import sqlite3


BASE_DIR = os.path.abspath(os.path.dirname("database.db"))

def dbConnection():
    connection = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))
    return connection