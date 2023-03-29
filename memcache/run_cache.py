from crypt import methods
from dataclasses import field
from tkinter import filedialog
from turtle import right
from PIL import Image
import io
import base64
from flask import Flask, request, json, jsonify
import requests
from .cache import LRUCache, RRCache, NOCache, Node
import mysql.connector
from frontend.connect_database import connect_to_database
import threading
from time import sleep
from memcache import webapp
from .cloudwatch import *
from .config import *
import time
import copy
import datetime

# @app.route("/")
# def update_other(self, data):
all_request = 0
counter = 0
hit = 0
miss = 0

# connect to db and get the current cache config
# so we mus run port 5000 first
my_db = connect_to_database()
operate_db = my_db.cursor()

operate_db.execute('SELECT * FROM `CACHE`')
a = operate_db.fetchone()
print(a)
capacity = int(a[1]) * 1000000
policy = a[2]
if policy == "RR":
    current_cache = RRCache(capacity)
elif policy == "LRU":
    current_cache = LRUCache(capacity)
else:
    current_cache = NOCache()


cloudwatch = boto3.resource('cloudwatch', region_name='us-east-1', aws_access_key_id='AKIAQG7ISCULW2SYVQF7', aws_secret_access_key='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')
cw = CloudWatchWrapper(cloudwatch)

def update_stats():
    num_items = len(current_cache.storage)
    total_size = current_cache.capacity - current_cache.available
    num_request = all_request
    miss_rate = miss/counter if counter != 0 else 0
    hit_rate = hit/counter if counter != 0 else 0
    cw.put_metric_data('A2cache', 'num', num_items, 'Count')
    cw.put_metric_data('A2cache', 'size', total_size, 'Count')
    cw.put_metric_data('A2cache', 'request', num_request, 'Count')
    cw.put_metric_data('A2cache', 'miss', miss_rate, 'Count')
    cw.put_metric_data('A2cache', 'hit', hit_rate, 'Count')
    cache_size = pool_size()
    cw.put_metric_data('A2cache', 'cache_size', cache_size, 'Count')
    

# # update status every 5 seconds
def daemon():
    while 1:
        update_stats()
        sleep(5)


x = threading.Thread(target=daemon)
x.start()


@webapp.route("/")
def hello_world():
    return "<title>actual memcache</title> <p>Hello, World!</p>"


@webapp.route("/get_metric_data")
def get_metric_data():
    d = {}
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=30)
    avg_num = cw.get_metric_statistics('A2cache', 'num', start_time, end_time, 60, ['Average'])
    avg_size = cw.get_metric_statistics('A2cache', 'size', start_time, end_time, 60, ['Average'])
    avg_request = cw.get_metric_statistics('A2cache', 'request', start_time, end_time, 60, ['Average'])
    avg_miss = cw.get_metric_statistics('A2cache', 'miss', start_time, end_time, 60, ['Average'])
    avg_hit = cw.get_metric_statistics('A2cache', 'hit', start_time, end_time, 60, ['Average'])
    d['num'] = avg_num
    d['size'] = avg_size
    d['request'] = avg_request
    d['miss'] = avg_miss
    d['hit'] = avg_hit
    print(d)
    return d


@webapp.route("/get_all_data", methods=['GET', 'POST'])
def get_all_data():
    l = []
    for i in current_cache.storage:
        print("the i in get_all_data is", i)
        d = {}
        d['key'] = i
        temp = current_cache.storage[i]
        print(temp)
        try:
            d['img_data'] = temp.val
        except:
            d['img_data'] = temp
        l.append(d)
    print("in get_all_data route, l is")
    print(l)
    return jsonify({'content': l})


@webapp.route('/get_status', methods=['GET'])
def get_status():
    print("hit:", current_cache.hit, 'miss:', current_cache.miss)
    return jsonify({"hit": current_cache.hit, 'miss': current_cache.miss})


# after clearing the current cache
# the items in the cache is dropped
# but the policy and capacity remains unchanged
@webapp.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    global counter, miss, hit
    counter, miss, hit = 0, 0, 0
    current_cache.clear()
    return jsonify({"success": "true"})


@webapp.route('/set_config', methods=['GET', 'POST'])
def set_config():
    policy = request.json.get('policy')
    capacity = int(request.json.get('capacity')) * 1000000
    print(capacity)
    # note the capacity is in MB, 
    # so we need to convert it to byte
    global current_cache
    if policy == "RR":
        current_cache = RRCache(capacity)
    else:
        current_cache = LRUCache(int(capacity))
    return jsonify({"success": "true", 'curr_cache_capacity': current_cache.capacity})


@webapp.route('/get_cache', methods=['POST'])
def get_file():
    global counter, miss, hit, all_request
    all_request += 1
    counter += 1
    fileID = request.json.get('key')
    file_data = current_cache.get(fileID)
    # print("current cache", current_cache.storage)
    if file_data == -1:
        miss += 1
        return jsonify({"success": "false", 'error': {'code': 1, 'message': 'file not in cache'}})
    else:
        hit += 1
        return jsonify({"success": "true", "content": file_data})


@webapp.route('/update_cache', methods=['POST'])
def update_cache():
    global all_request
    all_request += 1
    fileID = request.json.get('key')
    fileData = request.json.get('value')
    # print('file ID is', fileID, 'file data is', fileData)
    # print('current cache has', current_cache.storage)
    if current_cache.put(fileID, fileData) == -1:
        return jsonify({'success': "false", 'error': {'code': 1, 'message': 'file too big'}})
    else:
        return jsonify({"success": "true"})

# def daemon():
#     while 1:
#         sleep(5)
#         update_stats()

#get the total number of nodes
def pool_size():
    instances = get_all_running()
    lis = [instance for instance in instances]
    return len(lis)

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

