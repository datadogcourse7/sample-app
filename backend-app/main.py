import pymysql
from flask import Flask, render_template, request, redirect, jsonify
from flask_restful import Resource, Api
carsales = Flask(__name__)
api = Api(carsales)
from ddtrace.runtime import RuntimeMetrics
RuntimeMetrics.enable()
from ddtrace import tracer ## IN ORDER GENERATE 500 for backend service comment this line
import os
import json 
from ddtrace.runtime import RuntimeMetrics  ## Run Time https://docs.datadoghq.com/tracing/metrics/runtime_metrics/python/
RuntimeMetrics.enable()

def connection():
    s = 'mysqldb' #Your server(host) name
    d = 'flaskdb'
    u = 'root' #Your login user
    p = 'password' #Your login password
    conn = pymysql.connect(host=s, user=u, password=p, database=d)
    return conn


# https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/#no-standard-library-logging

from ddtrace import patch; patch(logging=True)
import logging
from ddtrace import tracer

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')



#logging.basicConfig(format=FORMAT)
#log = logging.getLogger(__name__)
#log.level = logging.INFO



#### https://docs.datadoghq.com/tracing/trace_pipeline/ingestion_mechanisms/?tab=python

## OR
#######  https://app.datadoghq.eu/apm/traces/ingestion-control?env=%2A&service=carlist-dev&start=1658654975993&end=1658658575993&paused=false

os.environ["DD_TRACE_SAMPLE_RATE"] = "0.1"
os.environ["DD_TRACE_SAMPLING_RULES"] = '[{"service": "backend-app", "sample_rate": 0.4}]'



#@tracer.wrap()
#def hello():
#    log.info('Hello, World!')
#    log.info('Hello, World!')


class CartsResource(Resource):
    def get(self):
        span = tracer.trace("sandwich.create", resource="resource_name")
        cars = []
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TblCars")
        for row in cursor.fetchall():
            cars.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
        conn.close()
        current_span = tracer.current_span()
        correlation_ids = (span.trace_id, span.span_id) if span else (None, None)
        if current_span:
            current_span.set_tag('customerlist', 'received')
        span.finish()


        span = tracer.current_span()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_format =logging.Formatter(json.dumps({'time':'%(asctime)s', 'name': '%(name)s', 'level': '%(levelname)s', 'message': '%(message)s', "event": "Trace context", "dd.trace_id": span.trace_id, "dd.span_id": span.span_id, "dd.env": "dev", "dd.service": "backend-app", "dd.version": "1.54"}))
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        logger.info({"event": "In tracer context", "dd.trace_id": span.trace_id, "dd.span_id": span.span_id, "dd.env": "dev", "dd.service": "backend-app", "dd.version": "1.54"})
        return cars

api.add_resource(CartsResource, '/clist')

if(__name__ == "__main__"):
    carsales.run(host="0.0.0.0",port=8000, debug=True)
