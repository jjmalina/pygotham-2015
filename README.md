# PyGotham 2015 - Building a Real-Time Analytics Service with InfluxDB

My slides and code for PyGotham 2015, which you can watch the video for [here](http://www.pyvideo.org/video/3815/building-a-real-time-analytics-service-with-influ).  

This all runs in Python 3 btw. Haven't tested Python 2.  

RTBTC is a Flask app that subscribes to the [Coinbase Exchange websocket feed](https://docs.exchange.coinbase.com/?python#websocket-feed) and writes data to InfluxDB.

## Installation

1 - Install InfluxDB

On Mac OS X:

```
$ brew update && brew install influxdb
$ influxd
```

On Ubuntu or Debian Linux:

```
$ wget http://influxdb.s3.amazonaws.com/influxdb_0.9.2_amd64.deb
$ sudo dpkg -i influxdb_0.9.2_amd64.deb
$ sudo /etc/init.d/influxdb start
```

2 - Install the requirements:

```
pip install -r requirements.txt
pip install git+git://github.com/jjmalina/pyinfluxql.git@master
pip install -e .
```

## Running the app

```
influxd -config=/path/to/influxdb.conf
influx -execute 'create database rtbtc;'

# ingest coinbase orders
python rtbtc/ingest.py

# run the HTTP server
python rtbtc/views.py
```