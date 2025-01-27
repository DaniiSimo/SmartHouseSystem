from typing import Tuple, Any

from base import Base


class GroupDeviceNetwork(Base):
    def __init__(self, name_network: str):
        super().__init__(name_network=name_network, subscribers_topics=[
            (f'{name_network}/bridge/response/group/members/#', 0),
        ])

    def init(self) -> None:
        self._client_mqtt.subscribe(f'{self._data_network["name"]}/bridge/groups')

    def __search_ids_device_and_group(self, name_group: str, address_ieee_device: str = None, name_device: str = None) -> tuple[None, None] | tuple[
        str, str]:
        data_group = self._client_db.get_data(table_name='group', filters={
            'name': {
                'value': name_group,
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
            return None, None
        data_group = data_group[0]

        data_filter = {
            'network_smart_house_id': {
                'value': self._data_network['id'],
                'operator_compare': '=',
                'operator_condition': 'AND'
            }
        }

        if address_ieee_device is not None:
            data_filter['address_ieee'] = {
                'value': address_ieee_device,
                'operator_compare': '=',
                'operator_condition': ''
            }

        if name_device is not None:
            if 'address_ieee' in data_filter:
                data_filter['address_ieee']['operator_condition'] = 'AND'
            data_filter['name'] = {
                'value': name_device,
                'operator_compare': '=',
                'operator_condition': ''
            }

        data_device = self._client_db.get_data(table_name='device_network', filters=data_filter)
        if len(data_device) == 0:
            return None, None
        data_device = data_device[0]

        return data_group['id'], data_device['id']

    def listen(self, message):
        action, response = super().listen(message)

        if action != 'groups' and response['status'] == 'error':
            return

        match action:
            case 'add':
                group_id, device_id = self.__search_ids_device_and_group(name_group=response['data']['group'], address_ieee_device=response['data']['device'])
                if group_id is None or device_id is None:
                    return

                self._client_db.add_data(table_name='group_device_network', data={
                    'group_id': group_id,
                    'device_network_id': device_id
                })
            case 'remove':
                group_id, device_id = self.__search_ids_device_and_group(name_group=response['data']['group'],
                                                                         name_device=response['data']['device'])
                if group_id is None or device_id is None:
                    return

                data_group_device_network = self._client_db.get_data(table_name='group_device_network', filters={
                    'device_network_id': {
                        'value': device_id,
                        'operator_compare': '=',
                        'operator_condition': 'AND'
                    },
                    'group_id': {
                        'value': group_id,
                        'operator_compare': '=',
                        'operator_condition': ''
                    },
                })
                if len(data_group_device_network) == 0:
                    return
                data_group_device_network = data_group_device_network[0]
                self._client_db.delete_data(table_name='group_device_network', record_id=data_group_device_network['id'])
            case 'groups':
                self._client_mqtt.unsubscribe(f'{self._data_network["name"]}/bridge/groups')
                for group in response:
                    if len(group['members']) == 0:
                        continue
                    for member in group['members']:
                        group_id, device_id = self.__search_ids_device_and_group(name_group=group['friendly_name'],
                                                                                 address_ieee_device=member['ieee_address'])
                        if group_id is None or device_id is None:
                            continue

                        self._client_db.add_data(table_name='group_device_network', data={
                            'group_id': group_id,
                            'device_network_id': device_id
                        })


groupDeviceNetwork = GroupDeviceNetwork(name_network="zigbee2mqtt")

groupDeviceNetwork.init()
input("Нажмите Enter, чтобы завершить...\n")
