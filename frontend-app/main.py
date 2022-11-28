import pymysql
from flask import Flask, render_template, request, redirect
import time
import requests
import os
carsales = Flask(__name__)


###################

from ddtrace.runtime import RuntimeMetrics
RuntimeMetrics.enable()
from ddtrace import tracer ## IN ORDER GENERATE 500 for addcar service comment this line

os.environ["DD_TRACE_SAMPLE_RATE"] = "0.1"
os.environ["DD_TRACE_SAMPLING_RULES"] = '[{"service": "frontend-app", "sample_rate": 0.3}]'

from ddtrace.runtime import RuntimeMetrics  ## Run Time https://docs.datadoghq.com/tracing/metrics/runtime_

def connection():
    s = 'mysqldb' #Your server(host) name
    d = 'flaskdb'
    u = 'root' #Your login user
    p = 'password' #Your login password
    conn = pymysql.connect(host=s, user=u, password=p, database=d)
    return conn


from ddtrace import patch; patch(logging=True)
import logging
from ddtrace import tracer

#FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
#          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
#          '- %(message)s')
#logging.basicConfig(format=FORMAT)
#log = logging.getLogger(__name__)
#log.level = logging.INFO

#@tracer.wrap()
#def hello():
#    log.info('Hello, World!')

#hello()


############## Adding custom tags




#from datadog_api_client import ApiClient, Configuration
#from datadog_api_client.v1.api.tags_api import TagsApi
#from datadog_api_client.v1.model.host_tags import HostTags

#body = HostTags(
#    host="test.host",
#    tags=[
#        "environment:myflask",
#    ],
#)

#configuration = Configuration()
#with ApiClient(configuration) as api_client:
#    api_instance = TagsApi(api_client)
#    response = api_instance.update_host_tags(host_name="host_name", body=body)


##############

#@tracer.wrap()


import logging
import json
#class JSONFormatter(logging.Formatter):
#        def __init__(self):
#                super().__init__()
#        def format(self, record):
#                record.msg = json.dumps(record.msg)
#                return super().format(record)

@carsales.route("/")
def main():
#    FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
#          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
#          '- %(message)s')
#    logging.basicConfig(format=FORMAT)
#    log = logging.getLogger(__name__)    
#    log.info("root endpoint")
    #logging.basicConfig(level=logging.INFO)
    span = tracer.current_span()
    

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format =logging.Formatter(json.dumps({'time':'%(asctime)s', 'name': '%(name)s', 'level': '%(levelname)s', 'message': '%(message)s', "event": "Trace context", "dd.trace_id": span.trace_id, "dd.span_id": span.span_id, "dd.env": "dev", "dd.service": "frontend-app", "dd.version": "1.54"}))
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    logger.info({"event": "In tracer context", "dd.trace_id": span.trace_id, "dd.span_id": span.span_id, "dd.env": "dev", "dd.service": "frontend-app", "dd.version": "1.54"})

    return render_template("welcome.html")




#@tracer.wrap()
@carsales.route("/showcarlist", methods = ['GET'])
def showcarlist():
    cars = []
    #cl = requests.get('http://addcar-dev:8000/clist')
    cl = requests.get('http://backend-app:8000/clist')
    for row in cl:
        cars.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
    #span = tracer.current_span()
    #correlation_ids = (span.trace_id, span.span_id) if span else (None, None)
    #FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
    #      '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
    #      '- %(message)s')
    #logging.basicConfig(format=FORMAT)
    #log = logging.getLogger(__name__)
    #log.level = logging.INFO
    #current_span = tracer.current_span()
    #span = tracer.current_span()
    #correlation_ids = (span.trace_id, span.span_id) if span else (None, None)
    
    #logger.info("showcarlist endpoint")
    #log.info('showcarlist')
    #import structlog
    #def tracer_injection(logger, log_method, event_dict):
    #    span = tracer.current_span()
    #    trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)
    #    event_dict['dd.trace_id'] = str(dd.trace_id or 0)
    #    event_dict['dd.span_id'] = str(dd.span_id or 0)
    #    event_dict['dd.env'] = ddtrace.config.env or ""
    #    event_dict['dd.service'] = ddtrace.config.service or ""
    #    event_dict['dd.version'] = ddtrace.config.version or ""
    #    return event_dict
    #structlog.configure(
    #    processors=[
    #        tracer_injection,
    #        structlog.processors.JSONRenderer()
    #    ]
    #)
    #log = structlog.get_logger()
    return render_template("carslist.html", cars = cars)


if(__name__ == "__main__"):
#    carsales.run(host="127.0.0.1",port=5000, debug=True)
    carsales.run(host="0.0.0.0",port=5000, debug=True)
