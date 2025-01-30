import sys

from base import Base
from server.python.app.moduleNeuralNetwork.services.client_mqtt import ClientMqtt
from server.python.app.moduleNeuralNetwork.services.enums.format_color import FormatColor
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.color import Color


class AudioQuery(Base):
    def __init__(self, name_network: str, key_word: str):
        super().__init__(name_network=name_network, subscribers_topics=[
            (f'audio/topic', 0),
        ])
        self.ieee_address_adding_device = None
        self.key_word = key_word

    def listen(self, message):
        query = message.payload.decode("utf-8")
        query = query.replace(self.key_word, '')
        clientMqtt = ClientMqtt('m8.wqtt.ru', 18992, 1, 'u_HHKIB8', '40g3qvlr')
        if 'включить лампочку' in query:
            try:
                clientMqtt.send_message('{"state": "ON"}', 'zigbee2mqtt/Лампочка Tuya 2/set')
            except Exception as e:
                print("Ошибка при отправке сообщения:", e)
        if 'выключить лампочку' in query:
            clientMqtt.send_message('{"state": "OFF"}', 'zigbee2mqtt/Лампочка Tuya 2/set')
        if 'поменять цвет' in query:
            text_color = query.split(' ')[-1]
            color_service = Color()
            hex_color = color_service.parse(value=text_color, result_format=FormatColor.HEX)
            clientMqtt.send_message('{"color": {"hex": "' + hex_color + '"}}', 'zigbee2mqtt/Лампочка Tuya 2/set')


audio_query = AudioQuery(name_network="zigbee2mqtt", key_word='альфа')

# device.init()
input("Нажмите Enter, чтобы завершить...\n")
