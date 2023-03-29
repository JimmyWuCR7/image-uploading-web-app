from fileinput import filename
import re
from flask import render_template, url_for, request
from app import webapp
from app import scaler_function as sf
import boto3
import requests
import mysql.connector
import time
from app import cloudwatch as cw
from datetime import datetime, timedelta


# connect to db

my_db = mysql.connector.connect(
    host="database-1.cpk7recyx32p.us-east-1.rds.amazonaws.com",
    user="admin",
    password="ece1779pass",
    database='ece1779_DB',
    port='3306')
operate_db = my_db.cursor()
@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/chart', methods=['GET'])
def chart():
    cloudwatch = boto3.resource('cloudwatch', region_name='us-east-1', aws_access_key_id='AKIAQG7ISCULW2SYVQF7', aws_secret_access_key='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')
    cw_wrapper = cw.CloudWatchWrapper(cloudwatch)
    end = datetime.utcnow()
    start = end - timedelta(minutes=30)
    #cache size
    cache_stats = cw_wrapper.get_metric_statistics(
        'A2cache', 'cache_size', start, end, 60,
        ['Maximum'])
    lis = cache_stats['Datapoints']
    sort_datetime(lis)
    print(lis)
    whole_cache = []
    time_cache = []
    print("item in lis:")
    for item in lis:
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(float(item['Maximum']))
        temp2.append(item['Timestamp'].year)
        temp2.append(item['Timestamp'].month)
        temp2.append(item['Timestamp'].day)
        temp2.append(item['Timestamp'].hour)
        temp2.append(item['Timestamp'].minute)
        whole_cache.append(temp)
        time_cache.append(temp2)
    
    #num of item
    num_stats = cw_wrapper.get_metric_statistics(
        'A2cache', 'num', start, end, 60,
        ['Sum'])
    lis = num_stats['Datapoints']
    sort_datetime(lis)
    print(lis)
    whole_num = []
    time_num = []
    print("item in lis:")
    for item in lis:
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(float(item['Sum']))
        temp2.append(item['Timestamp'].year)
        temp2.append(item['Timestamp'].month)
        temp2.append(item['Timestamp'].day)
        temp2.append(item['Timestamp'].hour)
        temp2.append(item['Timestamp'].minute)
        whole_num.append(temp)
        time_num.append(temp2)
    
    #size
    size_stats = cw_wrapper.get_metric_statistics(
        'A2cache', 'size', start, end, 60,
        ['Sum'])
    lis = size_stats['Datapoints']
    sort_datetime(lis)
    print(lis)
    whole_size = []
    time_size = []
    print("item in lis:")
    for item in lis:
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(float(item['Sum']))
        temp2.append(item['Timestamp'].year)
        temp2.append(item['Timestamp'].month)
        temp2.append(item['Timestamp'].day)
        temp2.append(item['Timestamp'].hour)
        temp2.append(item['Timestamp'].minute)
        whole_size.append(temp)
        time_size.append(temp2)

    #request
    request_stats = cw_wrapper.get_metric_statistics(
        'A2cache', 'request', start, end, 60,
        ['Sum'])
    lis = request_stats['Datapoints']
    sort_datetime(lis)
    print(lis)
    whole_req = []
    time_req = []
    print("item in lis:")
    for item in lis:
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(float(item['Sum']))
        temp2.append(item['Timestamp'].year)
        temp2.append(item['Timestamp'].month)
        temp2.append(item['Timestamp'].day)
        temp2.append(item['Timestamp'].hour)
        temp2.append(item['Timestamp'].minute)
        whole_req.append(temp)
        time_req.append(temp2)
    
    #miss
    miss_stats = cw_wrapper.get_metric_statistics(
        'A2cache', 'miss', start, end, 60,
        ['Average'])
    lis = miss_stats['Datapoints']
    sort_datetime(lis)
    print(lis)
    whole_miss = []
    time_miss = []
    print("item in lis:")
    for item in lis:
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(float(item['Average']))
        temp2.append(item['Timestamp'].year)
        temp2.append(item['Timestamp'].month)
        temp2.append(item['Timestamp'].day)
        temp2.append(item['Timestamp'].hour)
        temp2.append(item['Timestamp'].minute)
        whole_miss.append(temp)
        time_miss.append(temp2)

    #hit
    hit_stats = cw_wrapper.get_metric_statistics(
        'A2cache', 'hit', start, end, 60,
        ['Average'])
    lis = hit_stats['Datapoints']
    sort_datetime(lis)
    print(lis)
    whole_hit = []
    time_hit = []
    print("item in lis:")
    for item in lis:
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(float(item['Average']))
        temp2.append(item['Timestamp'].year)
        temp2.append(item['Timestamp'].month)
        temp2.append(item['Timestamp'].day)
        temp2.append(item['Timestamp'].hour)
        temp2.append(item['Timestamp'].minute)
        whole_hit.append(temp)
        time_hit.append(temp2)
    return render_template("chart.html", whole_num=whole_num, time_num=time_num, 
                                        whole_size=whole_size, time_size=time_size,
                                        whole_req=whole_req, time_req=time_req,
                                        whole_miss=whole_miss, time_miss=time_miss, 
                                        whole_hit=whole_hit, time_hit=time_hit,
                                        whole_cache=whole_cache, time_cache=time_cache)

@webapp.route('/config', methods=['GET', 'POST'])
def config():
    print('aaaaaaaaaa')
    pool_mode = ""
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters = [{'Name': 'instance-state-name', 'Values':['running']}]
    )
    my_list = [instance for instance in instances]
    num_instances = len(my_list)

    if "clear-button" in request.form:
        instances = sf.get_all_running()
        my_list = [instance for instance in instances]

        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket('ece1779-a2-test')
        print("begin to delete items on s3")
        my_bucket.objects.all().delete()
        print("finished delete items on s3")

        print("begin to delete items in cache")
        for instance in instances:
            if instance.id == "i-02c1c2ca435342caf":
                address = "http://127.0.0.1:5555/clear_cache"
            else:
                address = "http://" + instance.private_ip_address + ":5555/clear_cache"
            r = requests.post(address)
        print("finish delete items in cache")

        print("begin to delete items on rds")
        drop = '''DELETE FROM IMAGES'''
        operate_db.execute(drop)
        my_db.commit()
        print("finish to delete items on rds")
        return "data all cleared"

    if "auto" in request.form:
        pool_mode = "auto"
        print(pool_mode,request.form['max_rate'], request.form['min_rate'],request.form['exp_ratio'], request.form['shrink_ratio'])
        r = requests.post("http://127.0.0.1:5001/changeconfigure",
                          json={"mode": pool_mode,
                                'max_rate': request.form['max_rate'],
                                'min_rate': request.form['min_rate'],
                                'expand_ratio': request.form['exp_ratio'],
                                'shrink_ratio': request.form['shrink_ratio']}).json()
        return "mode switched to auto"

    if "manual" in request.form:
        pool_mode = "manual"
        r = requests.post("http://127.0.0.1:5001/changeconfigure",
                              json={"mode": pool_mode,
                                    'max_rate': 0,
                                    'min_rate': 0,
                                    'expand_ratio': 0,
                                    'shrink_ratio': 0}).json()
        return "mode switched to manual"

# get capacity and replacement policy, update to db
    if 'config_button' in request.form:
        print('begin of capacity and replace change')
        if request.form['capacity']:
            update_statement1 = '''UPDATE `CACHE`
                SET `capacity` = {0}
                WHERE `key` = '0'
            '''
            capacity = request.form['capacity']
            operate_db.execute(update_statement1.format(capacity))
            print('150')
        if request.form['replace']:
            update_statement2 = '''UPDATE `CACHE`
                SET `REPLACE` = '{0}'
                WHERE `key` = '0'
            '''
            policy = request.form['replace']
            operate_db.execute(update_statement2.format(policy))
            print('158')
        my_db.commit()
        print('160')
        instances = sf.get_all_running()
        print(instances)
        for instance in instances:
            if instance.id == "i-02c1c2ca435342caf":
                address = "http://127.0.0.1:5555/set_config"
            else:
                address = "http://" + instance.private_ip_address + ":5555/set_config"
            r = requests.post(address, json={"policy": request.form['replace'], 'capacity': request.form['capacity']}).json()
            print(r)
        return 'policy changed'

    if 'clear-cache' in request.form:
        instances = sf.get_all_running()
        for instance in instances:
            if instance.id == "i-02c1c2ca435342caf":
                address = "http://127.0.0.1:5555/clear_cache"
            else:
                address = "http://" + instance.private_ip_address + ":5555/clear_cache"
            r = requests.post(address)
        return "cache is cleared"

    if request.method == 'POST':
        if request.form['size-button'] == '+1':
            user_data_script = '''#!/bin/bash
            rm -rf /var/lib/cloud/*
            cd /home/ubuntu
            source venv/bin/activate
            pip install boto3
            cd ..
            cd /home/ubuntu/ECE-1779
            sh run_cache.sh >> /tmp/test.txt
            '''
            size = sf.pool_size()
            if size >= 8:
                return "The max number of node is 8"
            #get current storage
            data = sf.get_current_storage()
            print(data)

            instances = ec2.create_instances(
                ImageId= 'ami-0a19467cd021e807c',
                MinCount=1,
                MaxCount=1,
                SubnetId= 'subnet-0cd80dc587ddf903f',
                InstanceType="t2.micro",
                KeyName="a1-test",
                SecurityGroupIds=['sg-0d8d15b309a74f4ef', 'sg-0ae110a4709b47f6a'],
                UserData = user_data_script
            )
            instances[0].wait_until_running()
            instances[0].reload()
            sf.allocate_data(data)
            return "success"

        if request.form['size-button'] == '-1':
            size = sf.pool_size()
            if size <= 1:
                return "The min number of node is 1"
            data = sf.get_current_storage()
            print(data)
            instances = sf.get_all_running()
            for instance in instances:
                if instance.id != "i-02c1c2ca435342caf":
                    id = instance.id
                    ec2.instances.filter(InstanceIds=[id]).terminate()
                    break
            sf.allocate_data(data)
            return "success"

        # if request.form['clear-button'] == 'clear all data':
        #     s3_client = boto3.client("s3")
        #     response = s3_client.list_objects_v2(Bucket="ece1779-a2-test")
        #     files_in_folder = response["Contents"]
        #     files_to_delete = []
        #     # We will create Key array to pass to delete_objects function
        #     for f in files_in_folder:
        #         files_to_delete.append({"Key": f["Key"]})
        #     # This will delete all files in a folder
        #     response = s3_client.delete_objects(
        #         Bucket="ece1779-a2-test", Delete={"Objects": files_to_delete}
        #     )
        #     for instance in instances:
        #         if instance.id == "i-02c1c2ca435342caf":
        #             address = "http://127.0.0.1:5555/clear_cache"
        #         else:
        #             address = "http://" + instance.private_ip_address + ":5555/clear_cache"
        #         r = requests.post(address)
        #     return "data is cleared"


            # statement = '''
            #     SELECT * FROM `CACHE` WHERE `key`='0'
            # '''



    operate_db.execute('SELECT * FROM `CACHE`')
    a = operate_db.fetchone()
    
    return render_template("config.html", num_instances = num_instances, pool_mode = pool_mode, cap = a[1], rep = a[2])

def sort_datetime(lis):
    length = len(lis)

    for i in range(length):
        for j in range(0, length-i-1):
            if lis[j]['Timestamp'] > lis[j + 1]['Timestamp']:
                lis[j], lis[j + 1] = lis[j + 1], lis[j]