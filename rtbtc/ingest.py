# -*- coding: utf-8 -*-
"""
    rtbtc.ingest
    ~~~~~~~~~~~~

    Real time Coinbase trades and orders using their Websocket Feed
    https://docs.exchange.coinbase.com/?python#overview
"""

import asyncio
import json
import websockets

from rtbtc import create_app
from rtbtc.extensions import influxdb

application = create_app()

COINBASE_FEED_URL = "wss://ws-feed.exchange.coinbase.com"
BATCH_SIZE = 20


class BaseOrder(object):
    measurement = None

    def __init__(self, data):
        self.data = data
        self.time = data['time']
        self.tags = {
            'type': data['type'],
            'side': data['side']
        }

    def to_dict(self):
        return {
            'measurement': self.measurement,
            'tags': self.tags,
            'time': self.time,
            'fields': self.fields
        }


class Order(BaseOrder):
    """Represents a coinbase order"""

    measurement = 'orders'

    @property
    def fields(self):
        size = self.data.get('size') or self.data.get('remaining_size')
        return {
            'size': float(size) if size else None,
            'price': float(self.data['price']),
            'id': self.data['order_id']
        }


class Trade(BaseOrder):
    """Represents a coinbase trade"""

    measurement = 'trades'

    def __init__(self, data):
        super(Trade, self).__init__(data)
        self.tags = {
            'type': 'uptick' if data['side'] == 'sell' else 'downtick',
            'side': data['side']
        }

    @property
    def fields(self):
        size = float(self.data['size'])
        price = float(self.data['price'])
        return {
            'size': size,
            'price': price,
            'cost': size * price,
            'id': self.data['trade_id']
        }


@asyncio.coroutine
def coinbase_feed():
    websocket = yield from websockets.connect(COINBASE_FEED_URL)

    yield from websocket.send(json.dumps({
        "type": "subscribe",
        "product_id": "BTC-USD"
    }))

    points = []

    while True:
        message = yield from websocket.recv()
        event = json.loads(message)

        try:
            model = Trade if event['type'] == 'match' else Order
            points.append(model(event).to_dict())

            if len(points) > BATCH_SIZE:
                influxdb.write_points(points)  # a blocking call unfortunately
                application.logger.info("Wrote %i points" % len(points))
                points = []
        except Exception as e:
            application.logger.exception(e)


def main():
    try:
        asyncio.get_event_loop().run_until_complete(coinbase_feed())
    except:
        pass


if __name__ == '__main__':
    main()
