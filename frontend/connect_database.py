import mysql.connector
from flask import g
from .config import my_db

def connect_to_database():
    return mysql.connector.connect(user=my_db['user'],
                                   password=my_db['password'],
                                   host=my_db['host'],
                                   database=my_db['database'])

# TODO
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = connect_to_database()
#     return db