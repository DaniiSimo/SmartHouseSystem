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
import itertools
import yaml
import json
from server.python.app.moduleNeuralNetwork.services.db import DB
from server.python.app.moduleNeuralNetwork.services.generator_password import GeneratorPassword
from server.python.app.moduleNeuralNetwork.services.client_mqtt import ClientMqtt


def set_nested_value(d, keys, value):
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

normalization_service = Normalization()

NAME_NETWORK = 'zigbee2mqtt'
PATH_TO_DATA = Path(__file__).parent.parent.joinpath("data")

# region Подготовка данных о short commands
PATH_TO_DATA_SHORT_COMMAND = str(PATH_TO_DATA.joinpath("short_command.csv"))
shorts_commands = Reader.read_csv(PATH_TO_DATA_SHORT_COMMAND)
rule_short_command = []
data_short_command = {}
reverse_index_short_command = {}
for element in shorts_commands:
    key = ()
    words = []
    for word in element['short_command'].split(','):
        base_word = " ".join(normalization_service.lemmatization(word.lower().split())).strip()
        key = key + (base_word,)
        words.append(base_word)

    rule_short_command += words

    # region Сборка обратного индекса
    for word in words:
        reverse_index_short_command[word] = key
    # endregion

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
            set_nested_value(element_data, keys_data, element['param_value'])
        case 'color':
            set_nested_value(element_data, keys_data, '')
        case 'number':
            set_nested_value(element_data, keys_data, '')
            numerical_boundary = element['param_value'].split('-')
            element_short_command['allowed_values'] = range(int(numerical_boundary[0]), int(numerical_boundary[1]))
    element_short_command['data'] = element_data
    data_short_command[key] = element_short_command
rule_short_command = list(set(rule_short_command))
# endregion
PATH_TO_CONFIG = str(Path(__file__).parent.parent.joinpath("config").joinpath("link_db.yaml"))
PATH_TO_KEY = str(Path(__file__).parent.parent.joinpath("config").joinpath("secret.key"))

with open(PATH_TO_CONFIG, 'r', encoding='utf-8') as file:
    config_db = yaml.safe_load(file)
client_db = DB(db_name=config_db['db']['name'],
               user=config_db['db']['user'],
               password=config_db['db']['password'],
               host=config_db['db']['host'],
               port=config_db['db']['port'])
del config_db
data_network = client_db.get_data(table_name='network', filters={
    'name': {
        'value': name_network,
        'operator_compare': '=',
        'operator_condition': ''
    },
})

if len(data_network) == 0:
    raise Exception("No networks found")

return data_network[0]
# region Подготовка данных о конкретных device
data_network_devices = client_db.get_data(
    table_name='device_network',
    filters={
        'network_smart_house_id': {
            'value': data_network['id'],
            'operator_compare': '=',
            'operator_condition': ''
        }
    }
)
rule_specific_device = [
    " ".join(self.__normalization_service.lemmatization(row['name'].lower().split())).strip() for row in
    data_network_devices]
# endregion

# region Подготовка данных о сценариях
data_scripts = []

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