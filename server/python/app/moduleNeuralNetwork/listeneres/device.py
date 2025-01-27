from base import Base


class Device(Base):
    def __init__(self, name_network: str):
        super().__init__(name_network=name_network, subscribers_topics=[
            (f'{name_network}/bridge/response/device/#', 0),
            (f'{name_network}/bridge/event', 1),
        ])
        self.ieee_address_adding_device = None

    def init(self) -> None:
        self._client_mqtt.subscribe(f'{self._data_network["name"]}/bridge/devices')
    def __add_device_network(self, element:dict) -> None:
        if 'definition' not in element:
            return
        if 'model' not in element['definition']:
            return
        data_device = self._client_db.get_data(table_name='device', filters={
            'model': {
                'value': element['definition']['model'],
                'operator_compare': '=',
                'operator_condition': ''
            },
        })
        if len(data_device) == 0:
            return
        data_device = data_device[0]
        self._client_db.add_data(table_name='device_network', data={
            'name': element['friendly_name'],
            'address_ieee': element['ieee_address'],
            'device_id': data_device['id'],
            'network_smart_house_id': self._data_network['id']
        })
    def listen(self, message):
        action, response = super().listen(message)

        if action not in ['devices', 'event'] and response['status'] == 'error':
            return

        match action:
            case 'event':
                if 'type' not in response or 'data' not in response:
                    return
                if response['type'] != 'device_interview':
                    return
                if 'definition' not in response['data']:
                    return
                self.__add_device_network(element=response['data'])
            case 'remove':
                data_device = self._client_db.get_data(table_name='device_network', filters={
                    'name': {
                        'value': response['data']['id'],
                        'operator_compare': '=',
                        'operator_condition': 'AND'
                    },
                    'network_smart_house_id': {
                        'value': self._data_network['id'],
                        'operator_compare': '=',
                        'operator_condition': ''
                    }
                })
                if len(data_device) == 0:
                    return
                data_device = data_device[0]
                self._client_db.delete_data(table_name='device_network', record_id=data_device['id'])
            case 'rename':
                data_device = self._client_db.get_data(table_name='device_network', filters={
                    'name': {
                        'value': response['data']['from'],
                        'operator_compare': '=',
                        'operator_condition': 'AND'
                    },
                    'network_smart_house_id': {
                        'value': self._data_network['id'],
                        'operator_compare': '=',
                        'operator_condition': ''
                    }
                })
                if len(data_device) == 0:
                    return
                data_device = data_device[0]
                self._client_db.update_data(table_name='device_network', record_id=data_device['id'],
                                            new_data={'name': response['data']['to']})
            case 'devices':
                self._client_mqtt.unsubscribe(f'{self._data_network["name"]}/bridge/devices')
                for element in response:
                    self.__add_device_network(element=element)


device = Device(name_network="zigbee2mqtt")

#device.init()
input("Нажмите Enter, чтобы завершить...\n")
