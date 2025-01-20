# askme/gunicorn_conf.py

bind = "127.0.0.1:8000"
workers =  3
accesslog = './askme/askme.gunicorn.tag'
errorlog = './askme/askme.gunicorn.error.log'
loglevel = 'info'
