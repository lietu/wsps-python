# WSPS Python client

This is a Python client for [WSPS server](http://github.com/lietu/wsps-server).
 
WSPS stands for WebSocket Pub(lisher)-Sub(scriber), and that pretty much covers what it does. The WSPS server provides a WebSocket interface for clients to subscribe to messages on different "channels", and then publishing messages on those channels.

Licensed under MIT and new BSD licenses, more details in `LICENSE.txt`.


## Dependencies
 
This library uses ws4py, which can work just with threads, using Tornado, or
with Gevent. This library gives you the ability to use all of those options as
well, but if you plan on using Tornado or Gevent you will need to install a
compatible version yourself.

Currently the Gevent and Tornado client implementations are imaginary, but not
for long.


## Usage

### How to get it

With pip:
```
pip install wsps
```

Or easy_install:
```
easy_install wsps
```


### Example

This example assumes the WSPS server is running at localhost:52525.

The server `local_settings.py` should contain the following:

```python
LISTEN_PORT = 52525

SUBSCRIBE_KEYS = {
    r"some-channel": "subscribe-key"
}

PUBLISH_KEYS = {
    r"some-channel": "publish-key"
}

AUTHORIZATION_MANAGER = 'wspsserver.auth:SettingsAuthManager'
```

After that, this code should work:
```python
from time import sleep  # Not normally required
from wsps import WSPSClient  # Threaded client

subscribe_key = "subscribe-key"
publish_key = "publish-key"

def on_close(code, reason):
    print("Disconnected with code {}, reason was: {}".format(
        code, reason
    ))

def on_msg(packet):
    print("Got message: {}".format(packet.data["msg"]))

wsps = WSPSClient("ws://127.0.0.1:52525", on_close)
wsps.connect()
wsps.subscribe("some-channel", on_msg, subscribe_key)
sleep(0.25) # Normally you don't have to wait to subscribe to your own events
wsps.publish("some-channel", {"msg": "Hello, WSPS!"}, publish_key)
sleep(0.25) # Normally you also don't wait for events to arrive before quitting
wsps.disconnect()
```


## Improved performance via WSAccel

You can use [WSAccel](https://pypi.python.org/pypi/wsaccel) to improve the 
performance of the client, WSPS will dynamically patch the ws4py library with 
some optimized Cython code from it if it is available.

To install it just use pip:
```
pip install wsaccel
```
