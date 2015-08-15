# -*- coding: utf-8 -*-
"""
    rtbtc
    ~~~~~

    rtbtc: a real time bitcoin analytics app
"""

from . import factory


def create_app(**kwargs):
    return factory.create_app(__name__, **kwargs)
