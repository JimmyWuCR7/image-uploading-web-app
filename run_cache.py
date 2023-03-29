#!../venv/bin/python
from memcache.run_cache import webapp

webapp.run('0.0.0.0',5555,debug=True,threaded=True)
