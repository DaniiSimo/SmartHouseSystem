from base import Base
from server.python.app.moduleNeuralNetwork.services.client_mqtt import ClientMqtt
from server.python.app.moduleNeuralNetwork.services.enums.format_color import FormatColor
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.color import Color
from pathlib import Path
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from server.python.app.moduleNeuralNetwork.services.classificator import Classificator
from server.python.app.moduleNeuralNetwork.services.reader import Reader
from server.python.app.moduleNeuralNetwork.services.enums.format_color import FormatColor
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.color import Color
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.number import Number
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.date_and_time import DateAndTime
from server.python.app.moduleNeuralNetwork.services.normalization import Normalization
import json
import itertools


class AudioQuery(Base):
    def __init__(self, name_network: str, key_word: str):
        super().__init__(name_network=name_network, subscribers_topics=[
            (f'audio/topic', 0),
        ])
        self.ieee_address_adding_device = None
        self.key_word = key_word
        self.__normalization_service = Normalization()
        self.__classificator_service = Classificator()
        PATH_TO_DATA = Path(__file__).parent.parent.joinpath("data")

        # region Подготовка данных о short commands
        PATH_TO_DATA_SHORT_COMMAND = str(PATH_TO_DATA.joinpath("short_command.csv"))
        shorts_commands = Reader.read_csv(PATH_TO_DATA_SHORT_COMMAND)
        rule_short_command = []
        self.__data_short_command = {}
        self.__reverse_index_short_command = {}
        for element in shorts_commands:
            key = ()
            words = []
            for word in element['short_command'].split(','):
                base_word = " ".join(self.__normalization_service.lemmatization(word.lower().split())).strip()
                key = key + (base_word,)
                words.append(base_word)

            rule_short_command += words

            #region Сборка обратного индекса
            for word in words:
                self.__reverse_index_short_command[word] = key
            #endregion

            element_short_command = {
                'device': element['device'],
                'command': element['command'],
                'processing_value': element['processing_value'],
            }
            element_data = {}
            if '$' in element['param']:
                keys_data = element['param'].split('$')
            else:
                keys_data = [element['param']]
            match element['processing_value']:
                case None:
                    self.__set_nested_value(element_data,keys_data,element['param_value'])
                case 'color':
                    self.__set_nested_value(element_data, keys_data, '')
                case 'number':
                    self.__set_nested_value(element_data, keys_data, '')
                    numerical_boundary = element['param_value'].split('-')
                    element_short_command['allowed_values'] = range(int(numerical_boundary[0]), int(numerical_boundary[1]))
            element_short_command['data'] = element_data
            self.__data_short_command[key] = element_short_command
        rule_short_command = list(set(rule_short_command))
        # endregion

        # region Подготовка данных о абстрактных device
        PATH_TO_DATA_CLUSTERS_DEVICE = str(PATH_TO_DATA.joinpath("clusters_device.json"))
        data_clusters_device = Reader.read_json(PATH_TO_DATA_CLUSTERS_DEVICE)
        rule_abstract_device = []
        for element in data_clusters_device:
            rule_abstract_device += element['synonyms']
        rule_abstract_device = list(set(rule_abstract_device))
        # rule_abstract_device.append('включить')
        # rule_abstract_device.append('световой группа')
        # endregion

        # region Подготовка данных о конкретных device
        data_network_devices = self._client_db.get_data(
            table_name='device_network',
            filters={
                'network_smart_house_id': {
                    'value': self._data_network['id'],
                    'operator_compare': '=',
                    'operator_condition': ''
                }
            }
        )
        rule_specific_device = [
            " ".join(self.__normalization_service.lemmatization(row['name'].lower().split())).strip() for row in
            data_network_devices]
        # endregion

        # region Подготовка данных о группах
        data_networks_groups = self._client_db.get_data(
            table_name='group',
            filters={
                'network_smart_house_id': {
                    'value': self._data_network['id'],
                    'operator_compare': '=',
                    'operator_condition': ''
                }
            }
        )
        rule_groups = [" ".join(self.__normalization_service.lemmatization(row['name'].lower().split())).strip() for row
                       in data_networks_groups]
        # endregion

        # region Подготовка данных о цвете
        # color_service = Color()
        # colors = [" ".join(self.__normalization_service.lemmatization(color.split())).strip() for color in color_service.get_colors()]
        # k = 1
        # endregion

        # region Подготовка данных о сценариях
        self.__data_scripts = []

        if data_network_devices:
            ids_devices_network = [row['id'] for row in data_network_devices]
            self.__data_scripts += [{'сценарий ' + " ".join(
                self.__normalization_service.lemmatization(row['name'].lower().split())).strip(): {
                'id': row['script_id'],
                'name': [data_network_device['name'] for data_network_device in data_network_devices if
                         data_network_device.get('id') == row['device_network_id']][0]
            }} for row in self._client_db.get_data(
                table_name='script_device_network',
                filters={
                    'device_network_id': {
                        'value': ids_devices_network,
                        'operator_compare': 'IN',
                        'operator_condition': ''
                    }
                }
            )]
        if data_networks_groups:
            ids_groups_network = [row['id'] for row in data_networks_groups]
            self.__data_scripts += [{'сценарий ' + " ".join(
                self.__normalization_service.lemmatization(row['name'].lower().split())).strip(): {
                'id': row['script_id'],
                'name': [data_network_group['name'] for data_network_group in data_networks_groups if
                         data_network_group.get('id') == row['group_id']][0]
            }} for row
                in self._client_db.get_data(
                    table_name='script_group',
                    filters={
                        'group_id': {
                            'value': ids_groups_network,
                            'operator_compare': 'IN',
                            'operator_condition': ''
                        }
                    }
                )]
        rule_scripts = list({key for d in self.__data_scripts for key in d.keys()})
        # endregion

        self.__data_match = {
            "Короткая команда": rule_short_command,
            "Абстрактное устройство": rule_abstract_device,
            "Группа": rule_groups,
            'Сценарий': rule_scripts,
            'Конкретное устройство': rule_specific_device
        }

        self.__orders_rules = {
            "Короткая команда": 0,
            "Группа": 2,
            "Абстрактное устройство": 1,
            'Конкретное устройство': 2,
            'Сценарий': 2,
        }

    def __set_nested_value(self,d, keys, value):
        """
        Устанавливает значение в словаре d по вложенным ключам из списка keys.
        Если промежуточных словарей не существует, они будут созданы.

        :param d: исходный словарь
        :param keys: список ключей, например, ['data']
        :param value: значение, которое нужно установить
        """
        # Проходим по всем ключам, кроме последнего
        for key in keys[:-1]:
            d = d.setdefault(key, {})  # если ключа нет, создаём новый пустой словарь
        # Устанавливаем значение для последнего ключа
        d[keys[-1]] = value

    def listen(self, message):
        query = message.payload.decode("utf-8")
        #TODO Всё что до альфа нужно убрать
        query = query.replace(self.key_word, '')
        normalize_query = self.__normalization_service.normalize(raw_text=query)
        tokens = self.__classificator_service.classification(
            text_query=normalize_query,
            data_match=self.__data_match,
            create_new_words=True,
            orders_rules=self.__orders_rules)

        client_mqtt = self._create_client_mqtt()
        for token in tokens:
            match token['type']:
                case 'Короткая команда':
                    data_query = self.__data_short_command[
                        self.__reverse_index_short_command[token['token']]]
                    match data_query['processing_value']:
                        case None:
                            client_mqtt.send_message(json.dumps(data_query['data']),
                                             f'{self._data_network["name"]}/Лампочка Tuya 2/set')


                case 'Сценарий':
                    data_query = next((item[token['token']] for item in self.__data_scripts if token['token'] in item),
                                      None)
                    if data_query is not None:
                        client_mqtt.send_message('{"scene_recall":' + data_query["id"] + '}',
                                                 f'{self._data_network["name"]}/{data_query["name"]}/set')

        # if 'включить лампочку' in query:
        #     try:
        #         clientMqtt.send_message('{"state": "ON"}', 'zigbee2mqtt/Лампочка Tuya 2/set')
        #     except Exception as e:
        #         print("Ошибка при отправке сообщения:", e)
        # if 'выключить лампочку' in query:
        #     clientMqtt.send_message('{"state": "OFF"}', 'zigbee2mqtt/Лампочка Tuya 2/set')
        # if 'поменять цвет' in query:
        #     text_color = query.split(' ')[-1]
        #     color_service = Color()
        #     hex_color = color_service.parse(value=text_color, result_format=FormatColor.HEX)
        #     clientMqtt.send_message('{"color": {"hex": "' + hex_color + '"}}', 'zigbee2mqtt/Лампочка Tuya 2/set')


audio_query = AudioQuery(name_network="zigbee2mqtt", key_word='альфа')

# device.init()
input("Нажмите Enter, чтобы завершить...\n")
