from pathlib import Path
import yaml
import sys
import json

sys.path.insert(1, '../services')
from db import DB
from generator_password import GeneratorPassword
from client_mqtt import ClientMqtt


class Base:
    __PATH_TO_CONFIG = str(Path(__file__).parent.parent.joinpath("config").joinpath("link_db.yaml"))
    __PATH_TO_KEY = str(Path(__file__).parent.parent.joinpath("config").joinpath("secret.key"))

    def __init__(self, name_network: str, subscribers_topics: list):
        self._client_db = self.__init_client_db()
        self._data_network = self.__init_network(name_network=name_network)
        self._client_mqtt = self.__init_client_mqtt(subscribers_topics=subscribers_topics)

    def __init_client_db(self) -> DB:
        with open(self.__PATH_TO_CONFIG, 'r', encoding='utf-8') as file:
            config_db = yaml.safe_load(file)
        client_db = DB(db_name=config_db['db']['name'],
                       user=config_db['db']['user'],
                       password=config_db['db']['password'],
                       host=config_db['db']['host'],
                       port=config_db['db']['port'])
        del config_db
        return client_db

    def __init_network(self, name_network: str) -> dict:
        data_network = self._client_db.get_data(table_name='network', filters={
            'name': {
                'value': name_network,
                'operator_compare': '=',
                'operator_condition': ''
            },
        })

        if len(data_network) == 0:
            raise Exception("No networks found")

        return data_network[0]

    def __init_client_mqtt(self, subscribers_topics: list) -> ClientMqtt:
        data_mqtt = self._client_db.get_data(table_name='mqtt_broker', filters={
            'id': {
                'value': self._data_network['mqtt_broker_id'],
                'operator_compare': '=',
                'operator_condition': ''
            }
        })

        if len(data_mqtt) == 0:
            raise Exception("No setting mqtt found")

        data_mqtt = data_mqtt[0]
        # region Расшифровка пароля mqtt
        with open(self.__PATH_TO_KEY, 'rb') as file:
            key = file.read().strip()

        data_mqtt['password'] = GeneratorPassword.decrypt(secret_key=key, hash_password=data_mqtt["hash_password"])
        del key

        client_mqtt = ClientMqtt(
            host=data_mqtt['host'],
            port=data_mqtt['port'],
            username=data_mqtt['username'],
            password=data_mqtt['password'],
            callback=self.listen)

        client_mqtt.subscribe(subscribers_topics)

        return client_mqtt

    def listen(self, message):
        action = message.topic.replace(self._data_network['name'], '').split('/')[-1]
        response = json.loads(message.payload.decode("utf-8"))

        return action, response

