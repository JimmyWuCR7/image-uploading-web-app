from datetime import datetime, timedelta
from app import cloudwatch as cw
import boto3
import hashlib
from app import config
import requests
import time


#Create a EC2 Instance
#TODO: test the user_data
def create():
    ec2 = boto3.resource('ec2')
    script = '''#!/bin/bash
            rm -rf /var/lib/cloud/*
            cd /home/ubuntu
            source venv/bin/activate
            pip install boto3
            cd ..
            cd /home/ubuntu/ECE-1779
            sh run_cache.sh >> /tmp/test.txt
            '''
    #UserData=script
    instances = ec2.create_instances(ImageId=config.ami,
                                     MinCount=1,
                                     MaxCount=1,
                                     InstanceType='t2.micro',
                                     SubnetId=config.subnet,
                                     KeyName=config.keypair,
                                     SecurityGroupIds=config.security,
                                     UserData=script)
    return instances


#Terminate a EC2 Instance:
def terminate(instances_id):
    ec2 = boto3.resource('ec2')
    response = ec2.instances.filter(InstanceIds=[instances_id]).terminate()
    return response

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

#get the total number of nodes
def pool_size():
    instances = get_all_running()
    lis = [instance for instance in instances]
    return len(lis)

#Check whether there are instances that are still pending
def check_instance():
    instances = get_all_running()
    for instance in instances:
        if instance.state['Name'] == 'pending':
            return False
    return True

#read miss rate from CloudWatch
def read_current_stats():
    check = True
    while check:
        try:
            check = False
            cloudwatch = boto3.resource('cloudwatch', region_name='us-east-1', aws_access_key_id='AKIAQG7ISCULW2SYVQF7', aws_secret_access_key='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')
            cw_wrapper = cw.CloudWatchWrapper(cloudwatch)
            end = datetime.utcnow()
            start = end - timedelta(seconds=60)
            stats = cw_wrapper.get_metric_statistics(
                'A2cache', 'miss', start, end, 60,
                ['Average'])
            print(stats)
            stats = stats['Datapoints'][0]
            stats = stats['Average']
        except:
            check = True

    return float(stats)


#allocate the saved data
#data input: list of dicts of key & image path

def allocate_data(data):
    instances = get_all_running()
    length = pool_size()
    if check_instance():
        lis = [instance for instance in instances]
        sort(lis)
        print(lis)
        for i in data:
            partition = MD5(i["key"])
            if partition % length == 0:
                instance = lis[-1]
            else:
                instance = lis[partition % length - 1]
            if instance.id == "i-02c1c2ca435342caf":
                address = "http://127.0.0.1:5555/update_cache"
            else:
                address = "http://" + instance.private_ip_address + ":5555/update_cache"
            check = True
            while check:
                try:
                    check = False
                    r = requests.post(address, json={"key": i["key"], "value": i["img_data"]})
                except:
                    check = True
            print(r)

#get the current cache storage in the memcache pool
def get_current_storage():
    list_of_storage = []
    instances = get_all_running()
    for instance in instances:
        if instance.id == "i-02c1c2ca435342caf":
            address = "http://127.0.0.1:5555/get_all_data"
            address_clear = "http://127.0.0.1:5555/clear_cache"
        else:
            address = "http://" + instance.private_ip_address + ":5555/get_all_data"
            address_clear = "http://" + instance.private_ip_address + ":5555/clear_cache"
        temp_list = requests.post(address).json()['content']
        print(temp_list)
        list_of_storage = list_of_storage + temp_list
        re = requests.post(address_clear)
    return list_of_storage


#sort based on the instance id
def sort(lis):
    length = len(lis)

    for i in range(length):
        for j in range(0, length-i-1):
            if lis[j].id > lis[j + 1].id:
                lis[j], lis[j + 1] = lis[j + 1], lis[j]


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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
