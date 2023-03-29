import os, os.path
import re
from flask import request, render_template, url_for, redirect
# import pandas as pd
from PIL import Image
import io
from . import webapp, memcache
import mysql.connector
import requests
import base64
from ..config import *
from ..connect_database import connect_to_database
import boto3
import botocore
from .util_functions import * 
import hashlib

UPLOAD_FOLDER = './app/static'



#upload flask
@webapp.route('/show', methods=['GET', 'POST'])
def show():
    # connect to db
    file = ""
    path = 'static'
    my_db = connect_to_database()
    operate_db = my_db.cursor()

    if request.method == 'POST':
        if request.form['key'] == '':
            return 'Missing input'
        else:
            ec2 = boto3.resource('ec2')
            instances = ec2.instances.filter(
                Filters=[
                    {
                        'Name': 'instance-id',
                        'Values': [
                            'i-02c1c2ca435342caf'
                        ]
                    }
                ]
            )
            for instance in instances:
                print(instance.public_ip_address + ":5000/key/"+ request.form['key'])
                return redirect("key/"+ request.form['key'])
    return render_template('show.html', path = file)

def get_filename(file_name):
    return file_name

#return the corresponding partition of the input string
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

@webapp.route('/api/key/<key_value>', methods=['GET', 'POST'])
def api_search_result(key_value):
    # print("file name is",request.args.get('file_name'))
    # return key_value
    # check if key is in cache
    # if so, load it directly
    # return key_value
    print("/api/key/<key_value> 的 key", key_value)

    ########TODO:###########
    # get the MD5 partition and redirect to the corresponding route
    partition = MD5(key_value)
    ########################
    instances = get_all_running()
    lis = [instance for instance in instances]
    sort(lis)
    length = len(lis)
    if partition % length == 0:
        instance = lis[-1]
    else:
        instance = lis[partition % length - 1]
    if instance.id == 'i-02c1c2ca435342caf':
        address = "http://127.0.0.1:5555/get_cache"
        address2 = "http://127.0.0.1:5555/update_cache"
    else:
        address = "http://" + instance.private_ip_address + ":5555/get_cache"
        address2 = "http://" + instance.private_ip_address + ":5555/update_cache"


    r = requests.post(address, json={"key": key_value}).json()
    # print("/api/key/<key_value>", r)
    if r.get('success') == "true":
        content = r.get("content")
        # r1 = requests.post(address2, json={"key": key_value, "value": content})
        return r
    else:
        res = get_image(key_value)
        # print('get_image(key_value)', res)
        # r1 = requests.post(address2, json={"key": key_value, "value": res['content']})
        return res

@webapp.route('/key/<key_value>', methods=['GET', 'POST'])
def search_result(key_value):
    # print("file name is",request.args.get('file_name'))
    # return key_value
    # check if key is in cache
    # if so, load it directly
    # return key_value
    print("key/<key_value> 的 key", key_value)

    ########TODO:###########
    # get the MD5 partition and redirect to the corresponding route
    partition = MD5(key_value)
    ########################
    instances = get_all_running()
    lis = [instance for instance in instances]
    sort(lis)
    length = len(lis)
    if partition % length == 0:
        instance = lis[-1]
    else:
        instance = lis[partition % length - 1]
    if instance.id == 'i-02c1c2ca435342caf':
        address = "http://127.0.0.1:5555/get_cache"
        address2 = "http://127.0.0.1:5555/update_cache"
    else:
        address = "http://" + instance.private_ip_address + ":5555/get_cache"
        address2 = "http://" + instance.private_ip_address + ":5555/update_cache"


    r = requests.post(address, json={"key": key_value}).json()
    # print("/api/key/<key_value>", r)
    if r.get('success') == "true":
        content = r.get("content")
        r = requests.post(address2, json={"key": key_value, "value": content})
        return '<img src="data:image/png;base64,{}">'.format(content)
    else:
        res = get_image(key_value)
        print('get_image(key_value)', res)
        if res['success'] == 'true':
            r = requests.post(address2, json={"key": key_value, "value": res['content']})
            return '<img src="data:image/png;base64,{}">'.format(res['content'])
        else:
            return res


#sort based on the instance id
def sort(lis):
    length = len(lis)

    for i in range(length):
        for j in range(0, length-i-1):
            if lis[j].id > lis[j + 1].id:
                lis[j], lis[j + 1] = lis[j + 1], lis[j]

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
