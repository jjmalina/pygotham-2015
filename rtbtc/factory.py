# -*- coding: utf-8 -*-
"""
    rtbtc.factory
    ~~~~~~~~~~~~~

    rtbtc app factory
"""

import os
import six

from flask import Flask

from rtbtc.extensions import influxdb


def create_app(package_name, settings_override=None):
    app = Flask(package_name)
    app.config.from_object('rtbtc.settings')
    app.config.from_pyfile(
        os.environ.get(
            'SETTINGS_FILE',
            os.path.join(app.config['BASE_DIR'], 'instance', 'settings.cfg')
        ),
        silent=True
    )
    if settings_override:
        for key, value in six.iteritems(settings_override):
            if key.isupper():
                app.config[key] = value

    influxdb.init_app(app)

    return app
