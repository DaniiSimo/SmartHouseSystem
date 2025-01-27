from base import Base


class Group(Base):
    def __init__(self, name_network: str):
        super().__init__(name_network=name_network, subscribers_topics=[
            (f'{name_network}/bridge/response/group/+', 0),
        ])

    def init(self) -> None:
        self._client_mqtt.subscribe(f'{self._data_network["name"]}/bridge/groups')

    def listen(self, message):
        action, response = super().listen(message)

        if action != 'groups' and response['status'] == 'error':
            return

        match action:
            case 'add':
                self._client_db.add_data(table_name='group', data={
                    'name': response['data']['friendly_name'],
                    'group_id': response['data']['id'],
                    'network_smart_house_id': self._data_network['id']
                })
            case 'remove':
                data_group = self._client_db.get_data(table_name='group', filters={
                    'group_id': {
                        'value': response['data']['id'],
                        'operator_compare': '=',
                        'operator_condition': 'AND'
                    },
                    'network_smart_house_id': {
                        'value': self._data_network['id'],
                        'operator_compare': '=',
                        'operator_condition': ''
                    },
                })
                if len(data_group) == 0:
                    return
                data_group = data_group[0]
                self._client_db.delete_data(table_name='group', record_id=data_group['id'])
            case 'rename':
                data_group = self._client_db.get_data(table_name='group', filters={
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
                if len(data_group) == 0:
                    return
                data_group = data_group[0]
                self._client_db.update_data(table_name='group', record_id=data_group['id'],
                                            new_data={'name': response['data']['to']})
            case 'groups':
                self._client_mqtt.unsubscribe(f'{self._data_network["name"]}/bridge/groups')
                for element in response:
                    self._client_db.add_data(table_name='group', data={
                        'name': element['friendly_name'],
                        'group_id': element['id'],
                        'network_smart_house_id': self._data_network['id']
                    })
                print(response)


group = Group(name_network="zigbee2mqtt")

group.init()
input("Нажмите Enter, чтобы завершить...\n")
