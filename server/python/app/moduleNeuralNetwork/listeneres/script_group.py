from typing import Tuple, Any

from base import Base


class ScriptGroup(Base):
    def __init__(self, name_network: str):
        super().__init__(name_network=name_network, subscribers_topics=[
            (f'{name_network}/bridge/response/group/members/#', 0),
        ])

    def init(self) -> None:
        self._client_mqtt.subscribe(f'{self._data_network["name"]}/bridge/groups')

    def listen(self, message):
        action, response = super().listen(message)

        if action != 'groups' and response['status'] == 'error':
            return

        match action:
            case 'groups':
                self._client_mqtt.unsubscribe(f'{self._data_network["name"]}/bridge/groups')
                for group in response:
                    if len(group['scenes']) == 0:
                        continue
                    data_group = self._client_db.get_data(table_name='group', filters={
                        'name': {
                            'value': group['friendly_name'],
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
                        continue

                    group_id = data_group[0]['id']
                    for scene in group['scenes']:
                        self._client_db.add_data(table_name='script_group', data={
                            'group_id': group_id,
                            'script_id': scene['id'],
                            'name': scene['name']
                        })


scriptGroup = ScriptGroup(name_network="zigbee2mqtt")

scriptGroup.init()
input("Нажмите Enter, чтобы завершить...\n")
