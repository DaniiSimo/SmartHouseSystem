from pathlib import Path
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from classificator import Classificator
from reader import Reader
from server.python.app.moduleNeuralNetwork.services.enums.format_color import FormatColor
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.color import Color
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.number import Number
from server.python.app.moduleNeuralNetwork.services.processing_parameter_values.date_and_time import DateAndTime
from server.python.app.moduleNeuralNetwork.services.normalization import Normalization
import itertools


# Функция для проверки значений через GigaChat
def validate_parameter_values(parameter_values):
    messages = [
        SystemMessage(
            content="Ты помощник, который интерпретирует запросы пользователя, связанные с параметрами для устройств в умном доме. \
        У параметров могут быть следующие типы: numeric, enum, composite, binary, text, lock, switch, fan, list, light, cover, climate. \
        Например, яркость — numeric, цвет — enum, канал (например, на телевизоре) — numeric. \
        Если параметр принимает значение, отвечай односложно 'да' или 'нет'. Если команд несколько, отвечай для каждой команды отдельно. \
        Пример: параметр 'канал' может принимать значение '5'. Твой ответ: 'да'."
        )
    ]

    validated_params = {}
    for param, values in parameter_values.items():
        for value in values:
            user_input = f"Параметр {param} может принимать значение {value}?"
            messages.append(HumanMessage(content=user_input))

            res = chat(messages)
            messages.append(res)

            if res.content.strip().lower() == "да":
                if param not in validated_params:
                    validated_params[param] = []
                validated_params[param].append(value)

    return validated_params


PATH_TO_DATA = Path(__file__).parent.parent.joinpath("data")
# region Преобразование short commands
PATH_TO_DATA_SHORT_COMMAND = str(PATH_TO_DATA.joinpath("short_command.csv"))
data_short_command = Reader.read_csv(PATH_TO_DATA_SHORT_COMMAND)
rule_short_command = []
for element in data_short_command:
    rule_short_command += [word.lower() for word in element['short_command'].split(',')]
rule_short_command = list(set(rule_short_command))
# endregion

# region Преобразование device
PATH_TO_DATA_CLUSTERS_DEVICE = str(PATH_TO_DATA.joinpath("clusters_device.json"))
data_clusters_device = Reader.read_json(PATH_TO_DATA_CLUSTERS_DEVICE)
rule_device = []
for element in data_clusters_device:
    rule_device += element['synonyms']
rule_device = list(set(rule_device))
# endregion

# Инициализация GigaChat
# chat = GigaChat(
#     credentials='NjRmODUyMmEtOWY0ZS00OTU0LWJhYjAtZTZlNTlhYzAzZTliOjg1ZTc3Y2Q0LTgwMDctNGMzOC1hMGEwLTQ2MjlmYzgyMWYzZQ==',
#     verify_ssl_certs=False
# )
data_match = {
    "Короткая команда": rule_short_command,
    "Устройство": rule_device
}
# data_match = {
#     'Команда': ["включи", "активировать", "запустить", "задействовать", "подключить", "ввести в действие",
#                 "пустить в ход",
#                 "установить", "привести в действие", "снабдить", "оснастить", "погасить", "отключить", "выключать",
#                 "угасить", "прибить",
#                 "потушить", "перекрыть", "остановить", "затушить", "Увеличить", "увеличь", "повысить", "усилить",
#                 "добавить", "нарастить", "Уменьшить",
#                 "снизить", "понизь", "приглушить", "ослабить", "понизить", "уменьшить", "Изменить", "поменять",
#                 "сменить",
#                 "установить", "поставить",
#                 "переключить", "варьировать", "включить", 'влияние цвет на поведение'],
#     'Устройство': ["лампа", "лампочка", "светильник", "светодиод", "осветительный прибор", "электролампа", "свет",
#                    "Стереосистема", "музыкальный центр", "аудиосистема", "звуковая система", "музыкальная система",
#                    "звуковой центр",
#                    "телевизор", "тв", "телевизионный приёмник", "телевизионный аппарат", "телевизионное устройство",
#                    "телик",
#                    "ящик",
#                    "холодильная камера", "холодос", "холодильник", "рефрижератор", "холодильная установка", "холод",
#                    "холодильное оборудование",
#                    "холодильник", "Стиральная машина", "стиралка", "автоматическая стиральная машина",
#                    "бытовая стиральная машина", "машина для стирки",
#                    "Пылесос", "вакуумный очиститель", "уборочная машина", "пылеулавливатель", "пылеудалитель",
#                    "пылевсасыватель",
#                    "чайник", "электрочайник", "кипятильник", "заварочный чайник", "кухонный чайник",
#                    "нагревательный чайник",
#                    "Настольная лампа", "настольный светильник", "настольный осветитель", "лампа для стола",
#                    "рабочая лампа",
#                    "настольный фонарь", "настольная лампочка"
#                                         "Плита", "кухонная плита", "варочная плита", "варочная поверхность",
#                    "кухонная печь",
#                    "варочный агрегат", "Камера", "фотокамера", "видеокамера",
#                    "кинокамера", "камерный аппарат", "камерный блок", "фотоаппарат", "розетка", "электрическая розетка",
#                    "контакт", "розеточное гнездо", "электрический разъем",
#                    "электрический контакт"],
#     'Параметр': ["яркость", "цвет", "окраска", "время", "громкость", "температура", "режим", "канал", "программа"]
# }
query = 'Включать пожалуйста лампочку потом поменяй цвет на красный и включи режим огонь на сигнализации режим стоп'
normalization = Normalization()
normalize_query = normalization.normalize(raw_text=query)
classificator = Classificator()
tokens = classificator.classification(
    text_query=normalize_query,
    data_match=data_match,
    create_new_words=True)

parameter_values = {}
devices_params = {}
device_command_map = {}
current_command = None
current_parameter = None
current_device = None
current_room = None

for token in tokens:
    if token["type"] == "Команда":
        current_command = token["token"]  # Запоминаем текущую команду
    elif token["type"] == "Параметр":
        current_parameter = token["token"]
        if current_parameter not in parameter_values:
            parameter_values[current_parameter] = []
    elif token["type"] == "" and current_parameter:
        parameter_values[current_parameter].append(token["token"])
    elif token["type"] == "Устройство":
        current_device = token["token"]
        devices_params[current_device] = []
        if current_command:  # Если есть текущая команда, связываем ее с устройством
            device_command_map[current_device] = current_command
            current_command = None  # Сбрасываем команду после связывания

# Проверка значений через GigaChat
validated_params = validate_parameter_values(parameter_values)

print("Изначальные параметры и значения:", parameter_values)
print("Проверенные параметры и значения:", validated_params)
print("Устройства:", devices_params)
print("Команды для устройств:", device_command_map)

device_parameter_map = {
    "телик": ["громкость", "канал"],
    "лампочка": ["яркость", "цвет"],
}

device_parameter_values = {}

for device, params in devices_params.items():
    device_parameter_values[device] = {
        "command": device_command_map.get(device, None),  # Добавляем связанную команду
        "parameters": {}
    }

    # Добавляем только те параметры, которые поддерживаются данным устройством
    for param, values in validated_params.items():
        if param in device_parameter_map.get(device, []):  # Проверяем, поддерживает ли устройство этот параметр
            device_parameter_values[device]["parameters"][param] = values

# Выводим итоговые устройства с командами, параметрами, комнатами и их значениями
print("Устройства с командами, параметрами, их значениями и комнатами:")
for device, details in device_parameter_values.items():
    print(f"{device}: {details}")
