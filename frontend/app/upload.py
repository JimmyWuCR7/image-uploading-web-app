from cgi import print_environ, print_form
import os, os.path
from PIL import Image
import io
from flask import request, render_template, url_for
import pandas as pd
from . import webapp, memcache
import mysql.connector
import requests
import base64
from ..connect_database import connect_to_database
from .util_functions import * 

UPLOAD_FOLDER = './app/static'

# connect to db

my_db = connect_to_database()
operate_db = my_db.cursor()


#upload flask
@webapp.route('/api/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.form)
        if 'key' in request.form:
            key1 = request.form['key']
        else:
            key1 = request.data['key']
        r = upload_image(request, key1)
        return r
        # content = file1.read()
        # # print("type(content)", type(content))  
        # #get path
        # path = os.path.join(UPLOAD_FOLDER, file1.filename)
        # # if os.path.exists(path):
        # #     return 'The image has already been uploaded, or there is already a file with the same name'
        # #save file in the path
        # file2 = open(path, "wb")
        # file2.write(content)
        # file2.close()
        # # file2.save(path)
        # # file2.save(path)

        # #check if key already in db
        # statement = '''
        #     SELECT * FROM `IMAGES` WHERE `key`='{0}'
        # '''
        # operate_db.execute(statement.format(key1))
        # df_forcheck = pd.DataFrame(operate_db.fetchall(), columns=['key','path'])
        # if df_forcheck.empty:
        #     db_info = '''INSERT INTO `IMAGES` (`key`, `path`) VALUES ('{0}','{1}')'''
        #     operate_db.execute(db_info.format(key1, path))
        # else:
        #     update_statement = '''UPDATE `IMAGES`
        #         SET `path` = '{0}'
        #         WHERE `key` = '{1}'
        #     '''
        #     operate_db.execute(update_statement.format(path, key1))
        # my_db.commit()

        # print('request.files', request.files)
        # print("content is", content)

        #update cache
        # data = base64.b64encode(content).decode()
        # # print('data is:' , data)
        # # print("here is data:", type(data), "here is file1:", type(file1))
        # r = requests.post("http://127.0.0.1:5555/update_cache", json={"key": key1, "value": data})
        # print(r)
        return 'Upload successfully'

    return render_template('upload.html')
