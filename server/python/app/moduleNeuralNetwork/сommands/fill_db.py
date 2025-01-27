import re
import json
from pathlib import Path
import yaml
import sys

sys.path.insert(1, '../services')
from db import DB

PATH_TO_DATA = Path(__file__).parent.parent.joinpath("data")
PATH_TO_CONFIGS = Path(__file__).parent.parent.joinpath("config")
# region Подключение к бд
PATH_TO_CONFIG = str(PATH_TO_CONFIGS.joinpath("link_db.yaml"))
with open(PATH_TO_CONFIG, 'r', encoding='utf-8') as file:
    config_db = yaml.safe_load(file)

db = DB(db_name=config_db['db']['name'],
        user=config_db['db']['user'],
        password=config_db['db']['password'],
        host=config_db['db']['host'],
        port=config_db['db']['port'])
# endregion


# Открываем JSON файл
PATH_TO_DATA_DEVICE = str(PATH_TO_DATA.joinpath("data_devices.json"))
with open(PATH_TO_DATA_DEVICE, 'r', encoding='utf-8') as file:
    data = json.load(file)

for device in data.values():
    # region Заполнение таблицы devices
    id_device = db.add_data(
        table_name='device',
        data={
            'file_name': device['FileName'],
            'url': device['Url'],
            'vendor': device['Vendor'],
            'model': device['Model'],
            'description': device['Description'],
        },
    )
    for command in device['Exposes']:
        # region Заполнение общей таблицы command
        id_command = db.add_data(
            table_name='command',
            data={
                'device_id': id_device,
                'slug': command['Id'],
                'full_name': command['FullName'],
                'name': command['Name'],
                'endpoint': command['Endpoint'],
                'type': command['Type'],
                'is_read': command['IsRead']['IsEnabled'],
                'is_write': command['IsWrite']['IsEnabled']
            },
        )
        # endregion
        match command['Type']:
            case 'enum' | 'lock':
                for value in command['PossibleValues']:
                    db.add_data(
                        table_name=f'{command["Type"]}_command_value',
                        data={
                            'command_id': id_command,
                            'value': value,
                        }
                    )

            case 'binary':
                db.add_data(
                    table_name='binary_command_value',
                    data={
                        'command_id': id_command,
                        'value_equals': command['ValueEquals'],
                        'on_value': command['OnValue'],
                        'off_value': command['OffValue'],
                    },
                    return_column='command_id'
                )
            case 'numeric':
                db.add_data(
                    table_name='numeric_command_value',
                    data={
                        'command_id': id_command,
                        'unit': command['Unit'],
                        'min_value': command['MinValue'],
                        'max_value': command['MaxValue'],
                    },
                    return_column='command_id'
                )
            case 'composite':
                for payload in command['AnotherPayloadsValues']:
                    db.add_data(
                        table_name='composite_command_payload',
                        data={
                            'command_id': id_command,
                            'name': payload['Name'],
                            'type': payload['Type'],
                            'is_read': payload['IsRead']['IsEnabled'],
                            'is_write': payload['IsWrite']['IsEnabled']
                        }
                    )
            case 'switch':
                for object_command in command['IsWrite']['ObjectCommands']:
                    if command['Endpoint'] in object_command:
                        db.add_data(
                            table_name='switch_command_value',
                            data={
                                'command_id': id_command,
                                'value': object_command[command['Endpoint']]
                            }
                        )
            case 'text':
                if ('Example' in command or 'Format' in command) and (
                        command['Example'] is not None or command['Format'] is not None):
                    db.add_data(
                        table_name='text_command_value',
                        data={
                            'command_id': id_command,
                            'example': command['Example'] if 'Example' in command else None,
                            'format': command['Format'] if 'Format' in command else None,
                        },
                        return_column='command_id'
                    )
            case 'light':
                # region Обработка features
                features = command['Features']
                for indexFeature in range(0, len(features)):
                    feature = features[indexFeature]
                    data_feature = {
                        'device_id': id_device,
                        'slug': '',
                        'full_name': '',
                        'name': feature['Name'],
                        'endpoint': feature['Name'],
                        'type': '',
                        'is_read': feature['IsRead']['IsEnabled'],
                        'is_write': feature['IsWrite']['IsEnabled']
                    }
                    # region Обработка feature enum
                    if 'FollowingValues' in feature:
                        data_feature['type'] = 'enum'
                        id_feature = db.add_data(
                            table_name='command',
                            data=data_feature,
                        )
                        for value in feature['FollowingValues']:
                            db.add_data(
                                table_name=f'enum_command_value',
                                data={
                                    'command_id': id_feature,
                                    'value': value,
                                }
                            )
                        continue
                    # endregion
                    # region Обработка feature composite
                    alternative_values_keys = ['AlternativelyColors', 'AlternativelyHueOrSaturation']
                    existing_alternative_values_keys = [key for key in alternative_values_keys if
                                                        key in features[indexFeature]]
                    if len(existing_alternative_values_keys) > 0:
                        data_feature['type'] = 'composite'
                        id_feature = db.add_data(
                            table_name='command',
                            data=data_feature,
                        )
                        for element in feature[existing_alternative_values_keys[0]]:
                            pattern = r'^\s*\{\s*"' + features[indexFeature][
                                'Name'] + r'"\s*:\s*\{([^}]*)\}\s*\}\s*$'
                            match = re.match(pattern, element)
                            if not match:
                                continue
                            inner_content = match.group(1)
                            keys = re.findall(r'"(\w+)"\s*:', inner_content)
                            if not keys:
                                continue
                            for key in keys:
                                db.add_data(
                                    table_name='composite_command_payload',
                                    data={
                                        'command_id': id_feature,
                                        'name': key,
                                        'type': 'number',
                                        'is_read': True,
                                        'is_write': True
                                    }
                                )
                        continue
                    # endregion
                    # region Обработка feature number
                    if 'MinValue' in feature or 'MaxValue' in feature:
                        data_feature['type'] = 'numeric'
                        id_feature = db.add_data(
                            table_name='command',
                            data=data_feature,
                        )
                        db.add_data(
                            table_name='numeric_command_value',
                            data={
                                'command_id': id_feature,
                                'unit': feature['Unit'] if 'Unit' in feature else '',
                                'min_value': feature['MinValue'] if 'MinValue' in feature else '',
                                'max_value': feature['MaxValue'] if 'MaxValue' in feature else '',
                            },
                            return_column='command_id'
                        )
                        continue
                    # endregion
                    # region Обработка feature switch
                    data_feature['type'] = 'switch'
                    id_feature = db.add_data(
                        table_name='command',
                        data=data_feature,
                    )
                    for objectCommand in feature['IsWrite']['ObjectCommands']:
                        if feature['Name'] not in objectCommand:
                            feature['Name'] = next(iter(objectCommand), None)
                        if objectCommand[feature['Name']] not in ['', 'VALUE']:
                            db.add_data(
                                table_name='switch_command_value',
                                data={
                                    'command_id': id_feature,
                                    'value': objectCommand[feature['Name']]
                                }
                            )
                    # endregion
                # endregion


        # endregion

    # endregion
