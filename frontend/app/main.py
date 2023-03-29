from fileinput import filename
from ..app import webapp
from flask import render_template, url_for, request, Flask
from flask import json, jsonify
import mysql.connector
import os, os.path
from flask import request, jsonify
import os, os.path
import io
import pandas as pd
import mysql.connector
import requests
import base64
from ..connect_database import connect_to_database
import boto3
from botocore.config import Config
# from ..config import s3
UPLOAD_FOLDER = './static'

my_db = connect_to_database()
operate_db = my_db.cursor()
print("connected")

#################################################################
# resp = requests.get("http://169.254.169.254/latest/user-data/")
# conf_dict = json.loads(resp.content.decode('utf-8'))
# print(conf_dict)

# my_config = Config(
#     region_name = 'us-east-1',
#     #signature_version = 'v4',
#     retries = {
#         'max_attempts': 10,
#         'mode': 'standard'
#     }
# )
# s3 = boto3.client('s3', config=my_config, aws_access_key_id= 'AKIAUMOPR3NKHCETKZNC', aws_secret_access_key= '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')
# print(s3)
#################################################################


# create table if not exist
# drop = 'DROP TABLE IF EXISTS `CACHE`'
# operate_db.execute(drop)
# drop = 'DROP TABLE IF EXISTS IMAGES'
# operate_db.execute(drop)
# drop = 'DROP TABLE IF EXISTS CACHECHANGE'
# operate_db.execute(drop)
sql = '''CREATE TABLE IF NOT EXISTS `CACHE`(
        `KEY` CHAR(40) NOT NULL PRIMARY KEY,
        `CAPACITY` INT NOT NULL,
        `REPLACE` CHAR(40) NOT NULL
        )'''
operate_db.execute(sql)
sql2 = '''CREATE TABLE IF NOT EXISTS `IMAGES`(
            `KEY` CHAR(100) NOT NULL PRIMARY KEY,
            `PATH` CHAR(100) NOT NULL
            )'''
operate_db.execute(sql2)
my_db.commit()
sql3 = '''CREATE TABLE IF NOT EXISTS `CACHECHANGE`(
            `TIME` TIMESTAMP NOT NULL,
            `NUM` INT NOT NULL,
            `SIZE` INT NOT NULL,
            `REQUESTS` INT NOT NULL,
            `MISS` FLOAT NOT NULL,
            `HIT` FLOAT NOT NULL
            )'''
operate_db.execute(sql3)
print("tables created")
my_db.commit()

# try:
#     db_info = '''INSERT INTO `CACHE` (`key`, `capacity`, `replace`) VALUES ('0',500,'RR')'''
#     operate_db.execute(db_info)
#     my_db.commit()
# except:
#     pass

@webapp.route('/')
def main():
    return render_template("main.html")

# # TODO
# @webapp.route('/apii/upload', methods=['POST'])
# def upload():
#     # default err msg
#     # file: request.files['file'] from html

#     res = {"success": "false", "error": {"code": 'servererrorcode', "message": 'errormessage'}}
#     file = request.json['file']
#     key = request.json['key']
#     if not file or len(file) <= 128 or not key:
#         res['error']['code'] = 500
#         res['error']['message'] = 'missing input'
#         return jsonify(res)
#     file_name = file[:128].strip()
#     # print(key,file_name)
#     file_content_str = file[128:]
#     file_content = base64.b64decode(file_content_str.encode())
#     if not file_name.endswith(('.png', '.jpg', '.jpeg', '.heic')):
#         res['error']['code'] = 406
#         res['error']['message'] = 'Only png, jpg, jpeg, heic files are accepted'
#         return jsonify(res)

#     #check for duplicated file
#     path = os.path.join(UPLOAD_FOLDER, file_name)
#     # if os.path.exists(path):
#     #     res['error']['code'] = 406
#     #     res['error']['message'] = 'The image has already been uploaded, or there is already a file with the same name'
#     #     return jsonify(res)

#     #save file in the path since its been read
#     #which changes the file content
#     file2 = open(path, "wb")
#     file2.write(file_content)
#     file2.close()
#     #check if key in db
#     statement = '''
#         SELECT * FROM `IMAGES` WHERE `key`='{0}'
#     '''
#     operate_db.execute(statement.format(key))
#     df_forcheck = pd.DataFrame(operate_db.fetchall(), columns=['key','path'])
#     if df_forcheck.empty:
#         db_info = '''INSERT INTO `IMAGES` (`key`, `path`) VALUES ('{0}','{1}')'''
#         operate_db.execute(db_info.format(key, path))
#     else:
#         update_statement = '''UPDATE `IMAGES`
#             SET `path` = '{0}'
#             WHERE `key` = '{1}'
#         '''
#         operate_db.execute(update_statement.format(path, key))
#     my_db.commit()


#     r = requests.post("http://127.0.0.1:5555/update_cache", json={"key": key, "value": file_content_str}).json()
#     if r.get('success') == "true":
#         return jsonify({"success": "true"})
#     else:
#         res['error']['code'] = 406
#         res['error']['message'] = 'file too big for cache, please change capacity'
#         return jsonify(res)
        
@webapp.route('/api/list_keys', methods=['POST'])
def get_all_keys():
    operate_db.execute('''
    SELECT * FROM `IMAGES`
    ''')
    key_list = []
    for item in operate_db:
        key_list.append(item[0])
    return jsonify({"success": "true", "keys": key_list})

@webapp.route('/apii/key/<key_value>', methods=['POST'])
def get_key(key_value):
    res = {"success": "false", "error": {"code": 'servererrorcode', "message": 'errormessage'}}
    if not key_value:
        res['error']['code'] = 500
        res['error']['message'] = 'missing input'
        print('error')
        return jsonify(res)

    r = requests.post("http://127.0.0.1:5555/get_cache", json={"key": key_value}).json()
    if r.get('success') == "true":
        return jsonify({"success": "true", 'content': r.get('content')})
    # if not in cache, go look for it in database
    statement = '''
        SELECT * FROM `IMAGES` WHERE `key`='{0}'
    '''
    operate_db.execute(statement.format(key_value))
    row = operate_db.fetchone()
    if row == None:
        res['error']['code'] = 404
        res['error']['message'] = 'not found'
        return jsonify(res)
    path = row[1]
    # file = path.split("/",2)[1:][1]
    # the image is in database
    # retrieve the image data and put it in cache
    with open(path, "rb") as f:
        image_data = f.read()
    data = base64.b64encode(image_data).decode()
    r = requests.post("http://127.0.0.1:5555/update_cache", json={"key": key_value, "value": data})
    return jsonify({"success": "true", 'content': data})


    

