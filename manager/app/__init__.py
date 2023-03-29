from flask import Flask

global memcache

webapp = Flask(__name__)
memcache = {}


from app import main
from app import scaler_function
from app import cloudwatch
from app import config
