import os, os.path
from flask import request, render_template
from . import webapp, memcache
import mysql.connector
from..connect_database import connect_to_database

UPLOAD_FOLDER = './static'

#upload flask


@webapp.route('/api/list_keys', methods=['GET'])
def list_All():

    my_db = connect_to_database()
    operate_db = my_db.cursor()


    #get all item from table images
    operate_db.execute('''
        SELECT * FROM `IMAGES`
        ''')

    #get all keys
    key_list = []
    for item in operate_db:
        key_list.append(item[0])

    return render_template('list.html', title='All the Keys', key_list=key_list)