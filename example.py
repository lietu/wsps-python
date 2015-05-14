from time import sleep
from wsps import WSPSClient

if __name__ == "__main__":
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
    sleep(0.25)
    wsps.publish("some-channel", {"msg": "Hello, WSPS!"}, publish_key)
    sleep(0.25)
    wsps.disconnect()
