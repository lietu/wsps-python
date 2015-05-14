from ws4py.client.threadedclient import WebSocketClient


class WSPSThreadedClient(WebSocketClient):
    """
    Simple passthrough class to get messages from the ws4py threadedclient to
    WSPSClient.
    """

    def __init__(self, wsps_client, url):
        super(WSPSThreadedClient, self).__init__(url, protocols=['http-only'])
        self.wsps_client = wsps_client

    def closed(self, code, reason=None):
        """
        Called when connection is closed, relays info to WSPSClient

        :param int code: Error code
        :param str reason: Human readable message
        """

        self.wsps_client._on_close(code, reason)

    def received_message(self, message):
        """
        Called when server sends us a message, relays info to WSPSClient

        :param ws4py.TextMessage message: The message data
        """

        self.wsps_client._received_message(message)
