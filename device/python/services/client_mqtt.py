import paho.mqtt.client as mqtt


class ClientMqtt:
    def __init__(self, host: str, port: int, keepalive: int):
        self._client = mqtt.Client()
        self._client.connect(host, port, keepalive)
        self._client.loop_start()

    def send_message(self, data: any, topic: str):
        self._client.publish(topic, data)

    def __del__(self):
        self._client.loop_stop()
        self._client.disconnect()

