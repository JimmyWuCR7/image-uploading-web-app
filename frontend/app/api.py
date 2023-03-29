from flask import request, jsonify
from cgi import print_environ, print_form
import os, os.path
from PIL import Image
import io
import pandas as pd
from . import webapp, memcache
import mysql.connector
import requests
import base64
from ..connect_database import connect_to_database

UPLOAD_FOLDER = './static'

my_db = connect_to_database()
operate_db = my_db.cursor()

@webapp.route('/api/upload', methods=['POST'])
def upload():
    # default err msg
    # file: request.files['file'] from html
    file = request.form('file')
    key = request.form('key')
    res = {"success": "false", "error": {"code": 'servererrorcode', "message": 'errormessage'}}
    if not file.filename  or not key:
        res['error']['code'] = 500
        res['error']['message'] = 'missing input'
        return jsonify(res)
    filename = file.filename
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
        res['error']['code'] = 406
        res['error']['message'] = 'Only png, jpg, jpeg, heic files are accepted'
        return jsonify(res)

    content = file.read()
    #check for duplicated file
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        res['error']['code'] = 406
        res['error']['message'] = 'The image has already been uploaded, or there is already a file with the same name'
        return jsonify(res)

    #save file in the path since its been read
    #which changes the file content
    file2 = open(path, "wb")
    file2.write(content)
    file2.close()
    #check if key in db
    statement = '''
        SELECT * FROM `images` WHERE `key`='{0}'
    '''
    operate_db.execute(statement.format(key))
    df_forcheck = pd.DataFrame(operate_db.fetchall(), columns=['key','path'])
    if df_forcheck.empty:
        db_info = '''INSERT INTO `images` (`key`, `path`) VALUES ('{0}','{1}')'''
        operate_db.execute(db_info.format(key, path))
    else:
        orig_path = df_forcheck._get_value(0, 'path')
        try:
            os.remove(orig_path)
        except:
            pass
        update_statement = '''UPDATE `images`
            SET `path` = '{0}'
            WHERE `key` = '{1}'
        '''
        operate_db.execute(update_statement.format(path, key))
    my_db.commit()
    operate_db.execute('''
        SELECT * FROM `images`
    ''')
    df_result = pd.DataFrame(operate_db.fetchall(), columns=['key','path'])

    # print('request.files', request.files)
    # print("content is", content)
    data = base64.b64encode(content).decode()
    # print("here is data:", type(data), "here is file1:", type(file1))
    r = requests.post("http://127.0.0.1:5555/update_cache", json={"key": key, "value": data}).json()
    if r.get('success') == "true":
        return jsonify({"success": "true"})
    else:
        res['error']['code'] = 406
        res['error']['message'] = 'file too big for cache, please change capacity'
        return jsonify(res)
        
@webapp.route('/apii/list_keys', methods=['POST'])
def get_all_keys():
    operate_db.execute('''
    SELECT * FROM `images`
    ''')
    key_list = []
    for item in operate_db:
        key_list.append(item[0])
    return jsonify({"success": "true", "keys": key_list})

@webapp.route('/api/key/<key_value>', methods=['POST'])
def get_key():
    res = {"success": "false", "error": {"code": 'servererrorcode', "message": 'errormessage'}}
    if not request.form['key']:
        res['error']['code'] = 500
        res['error']['message'] = 'missing input'
        return jsonify(res)
    #get file and input key
    key1 = request.form['key']
    # check if key is in cache
    # if so, load it directly
    r = requests.post("http://127.0.0.1:5555/get_cache", json={"key": key1}).json()
    if r.get('success') == "true":
        return jsonify({"success": "true", 'content': r.get('content')})

    # if not in cache, go look for it in database
    statement = '''
        SELECT * FROM `images` WHERE `key`='{0}'
    '''
    operate_db.execute(statement.format(key1))
    row = operate_db.fetchone()
    if row == None:
        return 'Not found.'
    path = row[1]
    # file = path.split("/",2)[1:][1]
    # the image is in database
    # retrieve the image data and put it in cache
    with open(path, "rb") as f:
        image_data = f.read()
    data = base64.b64encode(image_data).decode()
    r = requests.post("http://127.0.0.1:5555/update_cache", json={"key": key1, "value": data})
    return jsonify({"success": "true", 'content': data})

