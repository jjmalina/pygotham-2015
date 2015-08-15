# -*- coding: utf-8 -*-
"""
    rtbtc.settings
    ~~~~~~~~~~~~~~

    default settings
"""

import os

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

"""
InfluxDB settings
"""
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DB = 'rtbtc'
