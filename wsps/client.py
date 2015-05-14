import json
from wsps.exceptions import *

# Auto-patch ws4py with wsaccel if that's available
try:
    import wsaccel

    wsaccel.patch_ws4py()
except ImportError:
    pass


# Different message types
SUBSCRIBE = "subscribe"
PUBLISH = "publish"
MESSAGE = "message"


class _WSPSPacket(object):
    """
    Packet coming from or going to the WSPS server.
    """

    # Extra properties for subclasses
    PROPERTIES = []

    def __init__(self, type, channel):
        self.type = type
        self.channel = channel

    def to_dict(self):
        """
        Get the full packet information as a dict.
        :returns dict:
        """
        data = {
            "type": self.type,
            "channel": self.channel
        }

        for prop in self.PROPERTIES:
            value = getattr(self, prop)
            if value is not None:
                data[prop] = value

        return data

    def to_json(self, pretty_print=True):
        """
        Get the full packet information as JSON
        :returns str:
        """

        return json.dumps(
            self.to_dict(),
            sort_keys=True if pretty_print else False,
            indent=4 if pretty_print else None
        )

    def __str__(self):
        """
        Convert the packet to a string
        """

        return self.to_json(False)


class _WSPSSubscribePacket(_WSPSPacket):
    """
    A subscribe packet, outgoing to the WSPS server.
    """

    PROPERTIES = ("key",)

    def __init__(self, channel, key=None):
        super(_WSPSSubscribePacket, self).__init__(
            SUBSCRIBE,
            channel
        )

        self.key = key


class _WSPSPublishPacket(_WSPSPacket):
    """
    A publish packet, outgoing to the WSPS server.
    """

    PROPERTIES = ("data", "key",)

    def __init__(self, channel, data, key=None):
        super(_WSPSPublishPacket, self).__init__(
            PUBLISH,
            channel
        )

        self.data = data
        self.key = key


class _WSPSMessagePacket(_WSPSPacket):
    """
    A message packet, incoming from the WSPS server.
    """

    PROPERTIES = ("data",)

    def __init__(self, channel, data):
        super(_WSPSMessagePacket, self).__init__(
            MESSAGE,
            channel
        )

        self.data = data


class _WSPSBaseClient(object):
    """
    Shared functionality of all WSPS clients, defines the common API.
    """

    def __init__(self, server, onclose=None):
        """
        :param server: Full URI of the destination WSPS server, e.g.
                       ws://localhost:52525/
        :param function onclose: Optional callback to run when connection is
                                 closed for any reason.
        """

        self.server = server
        self.onclose = onclose

        self._client = None
        self._subscribers = {}

    def connect(self):
        raise NotImplementedError("{cls} does not implement connect()".format(
            cls=self.__class__.__name__
        ))

    def disconnect(self):
        raise NotImplementedError("{cls} does not implement connect()".format(
            cls=self.__class__.__name__
        ))

    def publish(self, channel, data, key=None):
        """
        Publish a message to a channel.

        :param str channel: Name of the channel to publish to
        :param str|int|float|dict|list data: Stuff to send
        :param str key: Optional key if your WSPS server needs authorization
                        for the channel
        """
        packet = _WSPSPublishPacket(channel, data, key)
        self._send_packet(packet)

    def subscribe(self, channel, callback, key=None):
        """
        Register a callback to messages from a channel. You can register more
        than one callback per channel.

        :param str channel: Name of the channel to subscribe to
        :param function callback: Function that processes packets from this
                                  channel
        :param str key: Optional key if your WSPS server needs authorization
                        for the channel
        """
        if not channel in self._subscribers:
            self._subscribers[channel] = []

        self._subscribers[channel].append(callback)

        packet = _WSPSSubscribePacket(channel, key)
        self._send_packet(packet)

    def _on_close(self, code, reason=None):
        if self.onclose:
            self.onclose(code, reason)

    def _send_packet(self, packet):
        raise NotImplementedError(
            "{cls} does not implement _send_packet()".format(
                cls=self.__class__.__name__
            )
        )

    def _deliver_message_packet(self, packet):
        if packet.channel in self._subscribers:
            for callback in self._subscribers[packet.channel]:
                callback(packet)


class WSPSClient(_WSPSBaseClient):
    """
    WSPS Client using the ws4py builtin client, not terribly impressive, but
    doesn't depend on anything else.

    .. code-block:: python
        from wsps import WSPSClient

        client = WSPSClient("ws://127.0.0.1:52525")
        client.connect()

        def listener(packet):
            # Gotcha: will be called in a different thread.
            print(packet.to_json())

        client.subscribe("my-channel", listener)

        # If you want to receive your own messages (which normally you don't)
        # you could sleep and wait for the subscription to go through.

        client.publish("some-channel", "data")
    """

    def connect(self):
        """
        Connect to the WSPS server, starts the thread. Does not promise that
        connection is up immediately when this function returns.
        """

        if self._client:
            raise WSPSUsageError("This instance of WSPS client is already "
                                 "connected")

        from wsps.client_builtin import WSPSThreadedClient

        self._client = WSPSThreadedClient(self, self.server)
        self._client.connect()

    def disconnect(self, code=1000, reason="", wait=True):
        """
        Disconnect from the server.

        :param int code: Error code
        :param str reason: Human readable message
        :param bool wait: If we should wait for the thread to stop
        """

        self._client.close(code, reason)

        if wait:
            self._client.run_forever()

        self._client = None

    def _send_packet(self, packet):
        self._client.send(str(packet))

    def _received_message(self, message):
        data = json.loads(str(message))
        packet = _WSPSMessagePacket(data["channel"], data["data"])
        self._deliver_message_packet(packet)


class WSPSGeventClient(_WSPSBaseClient):
    """
    WSPS Client utilizing gevent.

    TODO: Write me
    """


class WSPSTornadoClient(_WSPSBaseClient):
    """
    WSPS Client utilizing Tornado

    TODO: Write me
    """

