#!../venv/bin/python

from frontend.app.main import webapp
#webapp.run('0.0.0.0',5000,debug=True,threaded=True)
webapp.run('0.0.0.0',5000,debug=False)