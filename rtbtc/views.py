# -*- coding: utf-8 -*-
"""
    rtbtc.views
    ~~~~~~~~~~~

    App views
"""

import dateutil
import functools
import json
from flask import make_response, request, Response, render_template
from werkzeug import exceptions as e

from pyinfluxql.functions import Mean
from pyinfluxql.query import Query
from pyinfluxql.utils import parse_interval

from rtbtc import create_app
from rtbtc.extensions import influxdb


app = create_app()


RESERVED_PARAMETERS = {'start', 'end', 'interval', 'order'}


class JSONException(e.HTTPException):
    def __init__(self, errors):
        self.errors = errors

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]

    def get_body(self, environ=None):
        return self.errors

    def get_response(self, environ=None):
        rv = json.dumps(self.get_body(environ), indent=2)
        return make_response(rv, self.code, self.get_headers(environ))


class BadRequest(JSONException, e.BadRequest):
    description = 'The browser/client sent a request that this server could not understand.'


class InvalidParameters(BadRequest):
    description = 'The request supplied invalid parameters.'


def process_time_parameter(request_params, name):
    dt = request_params.get(name)
    if dt:
        try:
            dt = dateutil.parser.parse(dt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=dateutil.tz.gettz('UTC'))
        except:
            raise e.InvalidParameters(errors=["'%s' is invalid" % name])
    return dt


def process_metrics_parameters(request_params):
    """Processes the request's querystring arguments to pass to a view function
    """
    start = process_time_parameter(request_params, 'start')
    end = process_time_parameter(request_params, 'end')

    if not start and not end:
        raise e.InvalidParameters(errors=['start and end are required'])

    interval = request_params.get('interval')
    if interval:
        try:
            interval = parse_interval(interval)
        except:
            raise e.InvalidParameters(
                errors=['"%s" is an invalid interval' % interval])

    order = request_params.get('order', 'desc')

    filters = {}
    for key in request_params.keys():
        val = request_params[key]
        if key not in RESERVED_PARAMETERS:
            if val == 'true' or val == 'false':
                val = val == 'true'
            filters[key] = val

    return start, end, interval, order, filters


def process_results(influxdb_results):
    series = influxdb_results.raw
    if series:
        return series['values']
    return []


@app.route('/')
def index():
    return render_template('index.html')


def metric_view(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        params = process_metrics_parameters(request.args)
        results = influxdb.engine.execute(view(*params))
        data = process_results(results)
        return Response(
            json.dumps(data),
            mimetype='application/json'
        )

    return wrapper


@app.route('/api/metrics/average_order_price')
@metric_view
def average_order_price(start, end, interval, order, filters):
    query = Query(Mean('price')) \
        .from_('orders') \
        .group_by(time=interval) \
        .date_range(start, end) \
        .where(**filters)
    return query


@app.route('/api/metrics/average_trade_price')
@metric_view
def average_trade_price(start, end, interval, order, filters):
    query = Query(Mean('price')) \
        .from_('trades') \
        .group_by(time=interval) \
        .date_range(start, end) \
        .where(**filters)
    return query


if __name__ == '__main__':
    app.run()
