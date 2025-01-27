import time

import paho.mqtt.client as mqtt


class ClientMqtt:
    def __init__(self, host: str, port: int, keepalive: int = 20, username: str = '', password: str = '', callback=None):
        self.callback = callback

        self._client = mqtt.Client(userdata=self.callback)
        self._client.username_pw_set(username, password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._connected = False
        self._client.connect(host, port, keepalive)
        self._client.loop_start()
        while not self._connected:
            time.sleep(0.1)  # Ждем, пока не установится соединение

    def _on_message(self, client, userdata, msg) -> None:
        if userdata:
            userdata(msg)  # вызываем функцию-обработчик
        # print(f"Получено сообщение с топика {msg.topic}: {msg.payload.decode()}")

    def _on_connect(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            self._connected = True
        else:
            raise (f"Ошибка соединения mqtt: {rc}")

    def subscribe(self, topic: str) -> mqtt.MQTTErrorCode:
        return self._client.subscribe(topic)[0]

    def unsubscribe(self, topic: str) -> mqtt.MQTTErrorCode:
        return self._client.unsubscribe(topic)[0]

    def send_message(self, data: any, topic: str) -> mqtt.MQTTErrorCode:
        result = self._client.publish(topic, data)
        result.wait_for_publish()
        return result.rc

    def __del__(self):
        self._client.loop_stop()
        self._client.disconnect()
