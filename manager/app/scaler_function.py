
import boto3
import hashlib
import requests
import time

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
