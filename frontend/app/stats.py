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
import datetime
from ..connect_database import connect_to_database


@webapp.route('/stats', methods=['GET'])
def stats():
    # connect to db
    my_db = connect_to_database()
    operate_db = my_db.cursor()

    #get current time
    current = datetime.datetime.now()
    ten_minute = datetime.timedelta(minutes=10)
    ten_min_ago = current - ten_minute

    query = '''
        SELECT * FROM `CACHECHANGE` ORDER BY TIME DESC
    '''
    operate_db.execute(query)

    #get statistics from database
    whole = []
    time = []
    count = 0
    for item in operate_db:
        if count > 120:
            break
        temp = []
        temp2 = []
        temp.append(0)
        temp.append(item[1])
        temp.append(item[2]/1000000)
        temp.append(item[3])
        temp.append(item[4])
        temp.append(item[5])
        temp2.append(item[0].year)
        temp2.append(item[0].month)
        temp2.append(item[0].day)
        temp2.append(item[0].hour)
        temp2.append(item[0].minute)
        temp2.append(item[0].second)
        whole.append(temp)
        time.append(temp2)
        count = count + 1

    return render_template('stats.html', title='Stats', whole=whole, time=time)