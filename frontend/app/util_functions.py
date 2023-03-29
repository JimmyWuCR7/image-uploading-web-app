from frontend.config import aws_config, UPLOAD_FOLDER, BUCKET
import os, requests, base64
from flask import request, jsonify
import tempfile, json
import boto3
from ..connect_database import connect_to_database
import pandas as pd
from ..config import *
import botocore
import hashlib

my_db = connect_to_database()
operate_db = my_db.cursor()
print("connected")


ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

s3 = boto3.client('s3')

def upload_image(request, key):
    # global backend_app
    #res = {"success": "false", "error": {"code": 'servererrorcode', "message": 'errormessage'}}
    file = request.files['file']
    # missing input
    if not file or not key:
        res['error']['code'] = 500
        res['error']['message'] = 'missing input'
        return jsonify(res)
    # wrong file format 
    if not file.filename.endswith(('.png', '.jpg', '.jpeg', '.heic')):
        res['error']['code'] = 406
        res['error']['message'] = 'Only png, jpg, jpeg, heic files are accepted'
        return jsonify(res)
    file_content = base64.b64encode(file.read())
    str_file_content = file_content.decode()
    s3.put_object(Body=file_content, Key=key, Bucket=BUCKET, ContentType='image')
    print("uploaded")
    #put cache in correct memcache
    print("begin put cache")
    instances = get_all_running()
    print(instances)
    lis = [instance for instance in instances]
    length = len(lis)
    print(lis)
    sort(lis)
    print(lis)
    
    partition = MD5(key)
    print(partition)
    if partition % length == 0:
        instance = lis[-1]
    else:
        instance = lis[partition % length - 1]
    print(instance.id)
    if instance.id == 'i-02c1c2ca435342caf':
        address = "http://127.0.0.1:5555/update_cache"
    else:
        address = "http://" + instance.private_ip_address + ":5555/update_cache"
    r = requests.post(address, json={"key": key, "value": str_file_content})
    url = 'https://{0}.s3.amazonaws.com/{1}'.format(BUCKET, key)
    print('url is', url)
    r2 = write_img_db(key, url)
    print(r2)
    return jsonify({"success": 'true'})
    # except:
    #     return jsonify(res)
    ########################
    # TODO
    # jsonReq={"keyReq":key}
    # ip_resp = requests.get('http://127.0.0.1:5555' + '/hash_key', json=jsonReq)
    # ip_dict = json.loads(ip_resp.content.decode('utf-8'))
    # ip=ip_dict[1]
    # res = requests.post('http://'+ str(ip) +':5000/invalidate', json=jsonReq)
    ########################
    # return write_img_db(key, key)
    



 

        # jsonReq={"keyReq":key}
        # ip_resp = requests.get(backend_app + '/hash_key', json=jsonReq)
        # ip_dict = json.loads(ip_resp.content.decode('utf-8'))
        # ip=ip_dict[1]
        # res = requests.post('http://'+ str(ip) +':5000/invalidate', json=jsonReq)
        # return write_img_db(key, key)

def write_img_db(image_key, image_path):
    """ Write image to DB
        Parameters:
            image_key (int): key value
            image_path (str): file name
        Return:
            response (str): "OK" or "ERROR"
    """
    statement = '''
        SELECT * FROM `IMAGES` WHERE `key`='{0}'
    '''
    print('trying to insert to db')
    operate_db.execute(statement.format(image_key))
    df_forcheck = pd.DataFrame(operate_db.fetchall(), columns=['key','path'])
    if df_forcheck.empty:
        db_info = '''INSERT INTO `IMAGES` (`key`, `path`) VALUES ('{0}','{1}')'''
        operate_db.execute(db_info.format(image_key, image_path))
    else:
        update_statement = '''UPDATE `IMAGES`
            SET `path` = '{0}'
            WHERE `key` = '{1}'
        '''
        operate_db.execute(update_statement.format(image_path, image_key))
    my_db.commit()
    return 'db updated'


def get_image(key):
    statement = '''
        SELECT * FROM `IMAGES` WHERE `key`='{0}'
    '''
    operate_db.execute(statement.format(key))
    row = operate_db.fetchone()
    if row == None:
        return {"success": "false", "error": {"code": 404, "message": 'tis picture not found in db'}}
    path = row[1]
    f = requests.get(path).content.decode('utf-8')
    print('f  is', f)
    return {"success": "true", "content": f}

#sort based on the instance id
def sort(lis):
    length = len(lis)

    for i in range(length):
        for j in range(0, length-i-1):
            if lis[j].id > lis[j + 1].id:
                lis[j], lis[j + 1] = lis[j + 1], lis[j]

#return partition based on MD5 hashing
def MD5(string):
    """
    >>> str = "k1"
    >>> result = MD5(str)
    >>> print(result)
    12
    """
    result = hashlib.md5(string.encode())
    MD5_result = result.hexdigest()
    if len(MD5_result) == 31:
        return 1
    else:
        return int(MD5_result[0], base=16) + 1

#Get all instance nodes running and starting in the pool
def get_all_running():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running', 'pending'
                ]
            }
        ]
    )
    return instances