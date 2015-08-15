# -*- coding: utf-8 -*-
"""
    rtbtc.extensions
    ~~~~~~~~~~

    Flask extensions
"""

from influxdb import InfluxDBClient, DataFrameClient

from pyinfluxql import Engine


class InfluxDBClientProxy(object):
    client_cls = DataFrameClient

    def __init__(self):
        self._client = None
        self._dfclient = None
        self.engine = None
        self.dfengine = None

    def init_app(self, app):
        client_args = (
            app.config['INFLUXDB_HOST'],
            app.config['INFLUXDB_PORT'],
            app.config['INFLUXDB_USER'],
            app.config['INFLUXDB_PASSWORD'],
            app.config['INFLUXDB_DB']
        )
        self._client = InfluxDBClient(*client_args)
        self._dfclient = DataFrameClient(*client_args)
        self.engine = Engine(self._client)
        self.dfengine = Engine(self._dfclient)

    def dfquery(self, query):
        return self._dfclient.query(query)

    def __getattr__(self, name):
        return getattr(self._client, name)


influxdb = InfluxDBClientProxy()
