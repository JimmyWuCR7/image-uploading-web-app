import time
from flask import request, jsonify
from app import scaler_function as sf
import threading
from app import webapp
from app import config

mode = 'manual'


#@webapp.route('/autoscaler', methods=['GET', 'POST'])
def autoscaler():
    while(True):
        instances = sf.get_all_running()
        if mode == 'auto':
            if sf.check_instance():
                length = sf.pool_size()
                current_miss_rate = sf.read_current_stats()
                print(current_miss_rate)

                if current_miss_rate > max_rate:
                    if length < 8:
                        data = sf.get_current_storage()

                        expand_num = round(length * expand_ratio)
                        if expand_num >= 8:
                            loop_num = 8
                        else:
                            loop_num = expand_num
                        for i in range(loop_num - length):
                            new_instances = sf.create()
                            new_instances[0].wait_until_running()
                            new_instances[0].reload()

                        sf.allocate_data(data)

                elif current_miss_rate < min_rate:
                    if length > 1:
                        data = sf.get_current_storage()
                        shrink_num = round(length * shrink_ratio)

                        if shrink_num <= 1:
                            loop_num = 1
                        else:
                            loop_num = shrink_num

                        count = 0
                        for instance in instances:
                            if count == (length - loop_num):
                                break
                            instance_id = instance.id
                            if instance_id != config.initial_instance_id:
                                response = sf.terminate(instance_id)
                                print(response)
                                count = count + 1
                        sf.allocate_data(data)
                else:
                    pass

            time.sleep(60)




@webapp.route('/changeconfigure', methods=['GET', 'POST'])
def changeconfigure():
    global mode, max_rate, min_rate, expand_ratio, shrink_ratio
    mode = request.json.get('mode')
    max_rate = float(request.json.get('max_rate'))
    min_rate = float(request.json.get('min_rate'))
    expand_ratio = float(request.json.get('expand_ratio'))
    shrink_ratio = float(request.json.get('shrink_ratio'))
    print(mode)
    print(max_rate)
    print(min_rate)
    print(expand_ratio)
    print(shrink_ratio)
    return jsonify({"success": "true"})

x = threading.Thread(target=autoscaler)
x.start()
