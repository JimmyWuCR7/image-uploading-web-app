from flask import Flask

global memcache

webapp = Flask(__name__)
memcache = {}

from ..app import main
from ..app import upload
from ..app import list
from ..app import show
from ..app import cache
from ..app import stats


#from app import main
#from app import upload
#from app import list
#from app import show
#from app import cache
#from app import stats


