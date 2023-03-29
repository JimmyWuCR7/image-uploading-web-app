from cgi import print_environ, print_form
import os, os.path
from PIL import Image
import io
from flask import request, render_template, url_for
from ..connect_database import connect_to_database

from . import webapp, memcache
import mysql.connector
import requests
import base64

UPLOAD_FOLDER = './app/static'

my_db = connect_to_database()
operate_db = my_db.cursor()


@webapp.route('/clear_cache',methods=['POST'])
def clear_cache():
    r = requests.post("http://127.0.0.1:5555/clear_cache")
    print(r)
    return 'cache is cleared'

# upload flask
@webapp.route('/cache', methods=['GET', 'POST'])
def cache_configure():
    if request.method == 'POST':
        #check some error situations
        if request.form['capacity'] == '' and request.form['replace'] == '':
            return 'Missing input.'
        if request.form['capacity'] != '' and int(request.form['capacity']) > 500:
            return 'Capacity cannot exceed 500MB.'
        if request.form['replace'] != '':
            if request.form['replace'] != 'LRU' and request.form['replace'] != 'RR':
                return 'Replacement Policy can only be LRU or RR.'

        # get capacity and replacement policy, update to db
        if request.form['capacity']:
            update_statement1 = '''UPDATE `CACHE`
                SET `capacity` = {0}
                WHERE `key` = '0'
            '''
            capacity = request.form['capacity']
            operate_db.execute(update_statement1.format(capacity))
        if request.form['replace']:
            update_statement2 = '''UPDATE `CACHE`
                SET `REPLACE` = '{0}'
                WHERE `key` = '0'
            '''
            policy = request.form['replace']
            operate_db.execute(update_statement2.format(policy))
        my_db.commit()

        #set configure to cache
        r = requests.post("http://127.0.0.1:5555/set_config", 
            json={"policy": request.form['replace'], 'capacity': request.form['capacity']}).json()

        return 'update successfully'

    statement = '''
        SELECT * FROM `CACHE` WHERE `key`='0'
    '''
    operate_db.execute(statement)
    row = operate_db.fetchone()

    #show capacity and replacement policy on browser
    capacity = row[1]
    replace = row[2]
    return render_template('cache.html', cap=capacity, rep=replace)

