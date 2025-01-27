import json
from pathlib import Path
import pandas as pd
import re

PATH_TO_DATA_DEVICE = str(Path(__file__).parent.parent.joinpath("data/data_devices.json"))
# Открываем JSON файл
with open(PATH_TO_DATA_DEVICE, 'r', encoding='utf-8') as file:
    data = json.load(file)  # Загружаем данные как словарь

# region Подготовка данных для значений различных типов
numeric = []
for key in data.keys():
    numeric += [{'Unit': expose['Unit'], 'MinValue': -9999 if expose['MinValue'] is None else expose['MinValue'],
                 'MaxValue': 9999 if expose['MaxValue'] is None else expose['MaxValue']} for expose in
                data[key]['Exposes'] if expose['Type'] == 'numeric']
numeric.append({'Unit': 'None', 'MinValue': -9999, 'MaxValue': 9999})
df = pd.DataFrame(numeric)
df['MinValue'] = pd.to_numeric(df['MinValue'], errors='coerce').fillna(0)
df['MaxValue'] = pd.to_numeric(df['MaxValue'], errors='coerce').fillna(0)
df['MinValue'] = df['MinValue'].astype(int)
df['MaxValue'] = df['MaxValue'].astype(int)
numeric_data = df.groupby('Unit').agg(
    MinValue=('MinValue', 'min'),
    MaxValue=('MaxValue', 'max')
).reset_index()
numeric_data.set_index('Unit', inplace=True)
numeric = numeric_data.to_dict(orient='index')
# endregion

for key in data.keys():
    new_exposes = {}
    for expose in data[key]['Exposes']:
        if not expose['IsRead']['IsEnabled'] and not expose['IsWrite']['IsEnabled']:
            continue
        del expose['Id'], expose['FullName'], expose['Name'], expose['Url']
        match expose['Type']:
            case 'numeric':
                key_default_value = str(expose['Unit'])
                min_value = numeric[key_default_value]['MinValue'] if expose['MinValue'] is None else expose['MinValue']
                max_value = numeric[key_default_value]['MaxValue'] if expose['MaxValue'] is None else expose['MaxValue']
                unit = expose['Unit'] if expose['Unit'] is not None else ''
                expose['values'] = [f'{min_value}{unit} - {max_value}{unit}']
                del expose['MinValue'], expose['MaxValue'], expose['Unit']
            case 'binary':
                del expose['OnValue'], expose['OffValue']
                values = expose['ValueEquals']
                values = re.findall(r'\b[A-Z]+\b', values)
                expose['values'] = values
                del expose['ValueEquals']
            case 'enum':
                expose['values'] = expose['PossibleValues']
                del expose['PossibleValues']

            case 'composite':
                another_data = expose.get('AnotherPayloadsValues', [])

                result = []

                # Обрабатываем данные
                for item in another_data:
                    name = item.get('Name')  # Извлекаем ключ 'Name'
                    item_type = item.get('Type')  # Извлекаем ключ 'Type'

                    if name is None or item_type is None:
                        print(f"Skipping invalid item: {item}")
                        continue

                    value = None  # Инициализируем значение

                    # Определяем значение в зависимости от типа
                    if item_type == 'numeric':
                        if name == 'strobe_duty_cycle':
                            value = ['1 - 10']
                        else:
                            value = ['1 - 9999']
                    elif item_type == 'enum':
                        if name == 'mode':
                            value = ['stop', 'burglar', 'fire', 'emergency', 'police_panic', 'fire_panic',
                                     'emergency_panic']
                        elif name == 'level':
                            value = ['low', 'medium', 'high', 'very_high']
                        elif name == 'strobe_level':
                            value = ['low', 'medium', 'high', 'very_high']
                        else:
                            value = []
                    elif item_type == 'binary':
                        if name == 'strobe':
                            value = ['true', 'false']
                        else:
                            value = ['true', 'false']

                    # Добавляем объект в результат
                    if value is not None:
                        result.append({'name': name, 'values': value})

                # Обновляем expose['values']
                expose['values'] = result
                del expose['AnotherPayloadsValues']
            case 'light':
                del expose['NameFeatures']
                # region Обработка features
                features = expose['Features']
                for indexFeature in range(0, len(features)):
                    # region Обработка чтения, записи и значений внутри записи
                    features[indexFeature]['read'] = features[indexFeature]['IsRead']['IsEnabled']
                    features[indexFeature]['write'] = features[indexFeature]['IsWrite']['IsEnabled']
                    features[indexFeature]['values'] = []
                    for objectCommand in features[indexFeature]['IsWrite']['ObjectCommands']:
                        if features[indexFeature]['Name'] not in objectCommand:
                            features[indexFeature]['Name'] = next(iter(objectCommand), None)
                        if objectCommand[features[indexFeature]['Name']] not in ['', 'VALUE']:
                            if type(objectCommand[features[indexFeature]['Name']]) is dict:
                                for keyValue in objectCommand[features[indexFeature]['Name']]:
                                    objectCommand[features[indexFeature]['Name']][keyValue] = ''
                            features[indexFeature]['values'].append(objectCommand[features[indexFeature]['Name']])
                    del features[indexFeature]['IsRead']
                    del features[indexFeature]['IsWrite']
                    # endregion
                    # region Обработка числовых данных
                    numberValue = (str(features[indexFeature]['MinValue']) + ' - ') if features[indexFeature].get(
                        'MinValue') is not None else '-9999 - '
                    if 'MinValue' in features[indexFeature]:
                        del features[indexFeature]['MinValue']
                    numberValue += str(features[indexFeature]['MaxValue']) if features[indexFeature].get(
                        'MaxValue') is not None else '9999'
                    if 'MaxValue' in features[indexFeature]:
                        del features[indexFeature]['MaxValue']
                    if numberValue != '-9999 - 9999':
                        features[indexFeature]['values'].append(numberValue)
                    # endregion
                    # region Обработка данных типа перечисления
                    if 'FollowingValues' in features[indexFeature]:
                        features[indexFeature]['values'] += features[indexFeature]['FollowingValues']
                        del features[indexFeature]['FollowingValues']
                    # endregion
                    # region Обработка Альтернативных значений
                    alternative_values_keys = ['AlternativelyColors', 'AlternativelyHueOrSaturation']
                    existing_alternative_values_keys = [key for key in alternative_values_keys if
                                                        key in features[indexFeature]]
                    if len(existing_alternative_values_keys) > 0:
                        for alternative_values_key in existing_alternative_values_keys:
                            for element in features[indexFeature][alternative_values_key]:
                                pattern = r'^\s*\{\s*"' + features[indexFeature][
                                    'Name'] + r'"\s*:\s*\{([^}]*)\}\s*\}\s*$'
                                match = re.match(pattern, element)
                                if not match:
                                    continue
                                inner_content = match.group(1)
                                keys = re.findall(r'"(\w+)"\s*:', inner_content)
                                if not keys:
                                    continue
                                features[indexFeature]['values'].append({key: "" for key in keys})
                            del features[indexFeature][alternative_values_key]
                    # endregion
                for feature in features:
                    new_exposes[feature['Name']] = {
                        'read': feature['read'],
                        'write': feature['write'],
                        'values': feature['values']
                    }
                continue
                # endregion
        # region Обработка read и write
        expose['read'] = expose['IsRead']['IsEnabled']
        expose['write'] = expose['IsWrite']['IsEnabled']
        del expose['IsRead'], expose['IsWrite']
        # endregion
        new_exposes[expose['Endpoint']] = expose
        del expose['Endpoint'], expose['Type']
    data[key] = new_exposes
