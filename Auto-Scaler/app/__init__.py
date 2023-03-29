from flask import Flask

webapp = Flask(__name__)

from app import app
from app import scaler_function
from app import config
from app import cloudwatch

