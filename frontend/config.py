import os, requests, json
from botocore.config import Config

# connect to db
my_db = {'host': 'database-1.cpk7recyx32p.us-east-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'ece1779pass',
        'database': 'ece1779_DB',
        'port': '3306'}


# TODO
aws_config = {
    'aws_access_key_id': 'AKIAUMOPR3NKHCETKZNC',
    'aws_secret_access_key': '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'
}
BUCKET = 'ece1779-a2-test'

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# max_capacity = 2
# replacement_policy = 'Least Recently Used'

URL_PREFIX = 'http://127.0.0.1:5000/'

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + 'frontend/static'

initial_instance_id = 'i-02c1c2ca435342caf'
