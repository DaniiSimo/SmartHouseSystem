import pandas as pd
from pathlib import Path
from itertools import chain

devices = [
    {
        'name': "Лампочка",
        'keywords': ["лампа", "светильник", "светодиод", "осветительный прибор", "электролампа", "свет"]
    },
    {
        'name': "Стереосистема",
        'keywords': ["музыкальный центр", "аудиосистема", "звуковая система", "музыкальная система", "звуковой центр",
                     "аудиоцентр", "стереоцентр", "стереоустановка"]
    },
    {
        'name': "Телевизор",
        'keywords': ["телевизор", "тв", "телевизионный приёмник", "телевизионный аппарат", "телевизионное устройство",
                     "экран"]
    },
    {
        'name': "Холодильник",
        'keywords': ["холодильная камера", "холодос", "холодильник", "рефрижератор",
                     "холодильная установка", "холод", "холодильное оборудование"]
    },
    {
        'name': "Стиральная машина",
        'keywords': ["стиралка", "автоматическая стиральная машина", "бытовая стиральная машина", "машина для стирки",
                     "прачечная машина", "стиральный автомат"]
    },
    {
        'name': "Пылесос",
        'keywords': ["вакуумный очиститель", "уборочная машина", "пылеулавливатель", "пылеудалитель", "пылевсасыватель",
                     "пылесосный аппарат"]
    },
    {
        'name': "Чайник",
        'keywords': ["электрочайник", "кипятильник", "заварочный чайник", "кухонный чайник", "нагревательный чайник",
                     "бытовой чайник"]
    },
    {
        'name': "Настольная лампа",
        'keywords': ["настольный светильник", "настольный осветитель", "лампа для стола", "рабочая лампа",
                     "настольный фонарь", "настольная лампочка"]
    },
    {
        'name': "Плита",
        'keywords': ["кухонная плита", "варочная плита", "варочная поверхность", "кухонная печь", "варочный агрегат",
                     "кухонное оборудование"]
    },
    {
        'name': "Камера",
        'keywords': ["фотокамера", "видеокамера", "кинокамера", "камерный аппарат", "камерный блок", "фотоаппарат"]
    },
    {
        'name': "Розетка",
        'keywords': ["электрическая розетка", "контакт", "розеточное гнездо", "электрический разъем",
                     "электрический контакт"]
    }
]

commands = [
    {  # 0
        "command": "Включить",
        "keywords": ["включить", "активировать", "запустить", "задействовать", "подключить", "ввести в действие",
                     "пустить в ход", "установить", "привести в действие", "снабдить", "оснастить"],
        "is_contain_parameters": True
    },
    {  # 1
        "command": "Выключить",
        "keywords": ["погасить", "отключить", "выключать", "угасить", "прибить", "потушить",
                     "перекрыть", "остановить", "затушить"],
        "is_contain_parameters": True
    },
    {  # 2
        "command": "Увеличить",
        "keywords": ["повысить", "усилить", "добавить", "нарастить"],
        "is_contain_parameters": True
    },
    {  # 3
        "command": "Уменьшить",
        "keywords": ["снизить", "приглушить", "ослабить", "понизить", "уменьшить"],
        "is_contain_parameters": True
    },
    {  # 4
        "command": "Изменить",
        "keywords": ["поменять", "сменить", "установить", "поставить", "переключить", "варьировать"],
        "is_contain_parameters": True
    },
    {  # 5
        "command": "Поставить на паузу",
        "keywords": ["приостановить", "остановить", "пауза", "задержать", "прервать", "поставить на стоп",
                     "сделать паузу", "застопорить"],
        "is_contain_parameters": True
    },
    {  # 6
        "command": "Возобновить воспроизведение",
        "keywords": ["продолжить воспроизведение", "восстановить воспроизведение", "снова воспроизвести",
                     "снова начать воспроизведение", "перезапустить воспроизведение", "возобновить проигрывание"],
        "is_contain_parameters": True
    },
    {  # 7
        "command": "Следующий трек",
        "keywords": ["следующая песня", "следующая композиция", "дальше", "вперед"],
        "is_contain_parameters": False
    },
    {  # 8
        "command": "Предыдущий трек",
        "keywords": ["предыдущая песня", "предыдущая композиция",
                     "назад", "предыдущий номер", "прошлый трек"],
        "is_contain_parameters": False
    },
    {  # 9
        "command": "Включить радио",
        "keywords": ["запустить радио", "воспроизводить радио", "поставить радио", "начать радиоэфир",
                     "включать радио", "включить радиостанция", "поставить радиоэфир"],
        "is_contain_parameters": False
    },
    {  # 10
        "command": "Включить CD",
        "keywords": ["запустить cd", "воспроизвести cd", "включить cd", "поставить cd", "начать проигрывание cd",
                     "включить диск", "поставить диск"],
        "is_contain_parameters": False
    },
    {  # 11
        "command": "Включить AUX",
        "keywords": ["запустить aux", "включить aux", "поставить aux", "начать aux", "воспроизвести aux"],
        "is_contain_parameters": False
    },
    {  # 12
        "command": "Переключиться на Bluetooth",
        "keywords": ["сменить на bluetooth", "переключить на bluetooth",
                     "сменить bluetooth", "переключить bluetooth", "переключиться bluetooth", "включить bluetooth"],
        "is_contain_parameters": False
    },
    {  # 13
        "command": "Включить повтор",
        "keywords": ["включить повторение", "включить репит", "поставить на повтор",
                     "запустить повтор", "активировать повторение"],
        "is_contain_parameters": False
    },
    {  # 14
        "command": "Выключить повтор",
        "keywords": ["отключить повторение", "выключить репит", "остановить повтор",
                     "выключить режим повтора", "деактивировать повторение"],
        "is_contain_parameters": False
    },
    {  # 15
        "command": "Включить случайное воспроизведение",
        "keywords": ["включить случайный режим", "запустить рандом",
                     "включить режим shuffle", "включить режим случайного воспроизведения"],
        "is_contain_parameters": False
    },
    {  # 16
        "command": "Выключить случайное воспроизведение",
        "keywords": ["отключить случайный режим", "выключить рандом",
                     "выключить режим shuffle", "выключить режим случайного воспроизведения"],
        "is_contain_parameters": False
    },
    {  # 17
        "command": "Включить свет",
        "keywords": ["включить освещение", "подать свет", "запустить освещение",
                     "включить фонарь"],
        "is_contain_parameters": False
    },
    {  # 18
        "command": "Выключить свет",
        "keywords": ["выключить освещение", "погасить свет", "отключить освещение",
                     "погасить лампу"],
        "is_contain_parameters": False
    },
    {  # 19
        "command": "Следующий канал",
        "keywords": ["другой канал", "вперед на канал", "переключить на следующий канал",
                     "дальше на канал", "следующий телепрограмма"],
        "is_contain_parameters": False
    },
    {  # 20
        "command": "Предыдущий канал",
        "keywords": ["предыдущий телеканал", "прошлый канал", "назад на канал",
                     "предыдущий телепрограмма", "вернуться на канал"],
        "is_contain_parameters": False
    },
    {  # 21
        "command": "Открыть люк",
        "keywords": ["распахнуть люк", "отпереть люк", "отворить люк", "отомкнуть люк", "раскрыть люк"],
        "is_contain_parameters": False
    },
    {  # 22
        "command": "Закрыть люк",
        "keywords": [
            "затворить люк", "запиреть люк", "захлопнуть люк", "заткнуть люк", "закупорить люк"
        ],
        "is_contain_parameters": False
    },
    {
        # 23
        "command": "Вернуться на базу",
        "keywords": [
            "возвратиться на базу", "сходить на базу",
            "съездитьна базу", "воротиться на базу"
        ],
        "is_contain_parameters": False
    },
    {  # 24
        "command": "Очистить мешок",
        "keywords": [
            "прочистить мешок", "выскресть мешок",
            "прибрать мешок", "вымыть мешок", "вычистить мешок"
        ],
        "is_contain_parameters": False
    },
    {

    },
    {
        # 26
        "command": "Зарядить батарею",
        "keywords": [
            "увеличить батарею", "наполнить батарею", "пополнить батарею",
            "зарядить акумулятор", "восполнить уровень заряда", "восполнить батарею"
        ],
        "is_contain_parameters": False
    },
    {

    },
    {
        # 28
        "command": "Держать",
        "keywords": ["удерживать", "держаться", "поддерживать",
                     "сохранять", "сохраняться", "хранить"],
        "is_contain_parameters": True

    },
    {
        # 29
        "command": "Повернуть",
        "keywords": [
            "крутануть",
            "развернуть", "перевести",
            "загнуть"
        ],
        "is_contain_parameters": True
    },
    {
        # 30
        "command": "Наклонить ",
        "keywords": [
            "склонить ",
            "нагнуть", "преклонить",
            "накренить", "опустить"
        ],
        "is_contain_parameters": True
    },
    {
        # 31
        "command": "Включить духовку",
        "keywords": [
            "активировать духовку", "запустить духовку", "задействовать духовку",
            "ввести в действие духовку", "привести в действие духовку"
        ],
        "is_contain_parameters": False
    },
    {
        # 32
        "command": "Выключить духовку",
        "keywords": [
            "погасить духовку", "остановить духовку",
            "потушить духовку"
        ],
        "is_contain_parameters": False
    },
    {
        # 33
        "command": "Сделать снимок",
        "keywords": [
            "сфотографировать", "сделать фото",
            "сделать кадр", "сфоткать", "щелкнуть", "запечатлить"
        ],
        "is_contain_parameters": False
    },
    {
        # 34
        "command": "Включить микрофон",
        "keywords": [
            "активировать микрофон", "включить аудиозапись",
            "включить запись звука", "включить аудио", "записать звук"
        ],
        "is_contain_parameters": False
    },
    {
        # 35
        "command": "Выключить микрофон",
        "keywords": [
            "деактивировать микрофон", "выключить аудиозапись",
            "выключить запись звука", "выключить аудио", "прекратить запись звука",
            "остановить аудиозапись", "прекратить аудиозапись"
        ],
        "is_contain_parameters": False
    },
    {
        # 36
        "command": "Включить динамик",
        "keywords": [
            "включить звук", "активировать динамик",
            "включить аудиовыход", "включить аудио"
        ],
        "is_contain_parameters": False
    },
    {
        # 37
        "command": "Выключить динамик",
        "keywords": [
            "выключить звук", "деактивировать динамик",
            "выключить аудиовыход", "выключить аудио"
        ],
        "is_contain_parameters": False
    },
]
smart_devices_and_commands = [
    {
        "id": 0,
        "id_device": 0,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 1,
        "id_device": 0,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 2,
        "id_device": 0,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 3,
        "id_device": 0,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 4,
        "id_device": 0,
        "id_command": 4,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 5,
        "id_device": 1,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 6,
        "id_device": 1,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 7,
        "id_device": 1,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 8,
        "id_device": 1,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 9,
        "id_device": 1,
        "id_command": 5,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 10,
        "id_device": 1,
        "id_command": 6,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 11,
        "id_device": 1,
        "id_command": 7,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 12,
        "id_device": 1,
        "id_command": 8,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 13,
        "id_device": 1,
        "id_command": 9,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 14,
        "id_device": 1,
        "id_command": 10,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 15,
        "id_device": 1,
        "id_command": 11,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 16,
        "id_device": 1,
        "id_command": 12,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 17,
        "id_device": 1,
        "id_command": 13,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 18,
        "id_device": 1,
        "id_command": 14,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 19,
        "id_device": 1,
        "id_command": 15,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 20,
        "id_device": 1,
        "id_command": 16,
        "it_can_exist_without_parameters": True
    },
    {  # 21
        "id": 21,
        "id_device": 3,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 22,
        "id_device": 3,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 23,
        "id_device": 3,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 24,
        "id_device": 3,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 25,
        "id_device": 3,
        "id_command": 17,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 26,
        "id_device": 3,
        "id_command": 18,
        "it_can_exist_without_parameters": True
    },
    {  # 27
        "id": 27,
        "id_device": 2,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 28,
        "id_device": 2,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 29,
        "id_device": 2,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 30,
        "id_device": 2,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 31,
        "id_device": 2,
        "id_command": 4,
        "it_can_exist_without_parameters": False
    },
    {
        "id": 32,
        "id_device": 2,
        "id_command": 19,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 33,
        "id_device": 2,
        "id_command": 20,
        "it_can_exist_without_parameters": True
    },
    {  # 34
        "id": 34,
        "id_device": 4,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 35,
        "id_device": 4,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {
        "id": 36,
        "id_device": 4,
        "id_command": 4,
        "it_can_exist_without_parameters": False
    },
    {  # 37
        "id": 37,
        "id_device": 4,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {  # 38
        "id": 38,
        "id_device": 4,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {  # 39
        "id": 39,
        "id_device": 4,
        "id_command": 21,
        "it_can_exist_without_parameters": True
    },
    {  # 40
        "id": 40,
        "id_device": 4,
        "id_command": 22,
        "it_can_exist_without_parameters": True
    },
    {  # 41
        "id": 41,
        "id_device": 5,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {  # 42
        "id": 42,
        "id_device": 5,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {  # 43
        "id": 43,
        "id_device": 5,
        "id_command": 23,
        "it_can_exist_without_parameters": True
    },
    {  # 44
        "id": 44,
        "id_device": 5,
        "id_command": 24,
        "it_can_exist_without_parameters": True
    },
    {  # 45

    },
    {  # 46
        "id": 46,
        "id_device": 5,
        "id_command": 26,
        "it_can_exist_without_parameters": True
    },
    {  # 47
        "id": 47,
        "id_device": 6,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {  # 48
        "id": 48,
        "id_device": 6,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {  # 49

    },
    {  # 50
        "id": 50,
        "id_device": 6,
        "id_command": 28,
        "it_can_exist_without_parameters": False
    },
    {  # 51
        "id": 51,
        "id_device": 7,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {  # 52
        "id": 52,
        "id_device": 7,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {  # 53
        "id": 53,
        "id_device": 7,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {  # 54
        "id": 54,
        "id_device": 7,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {  # 55
        "id": 55,
        "id_device": 7,
        "id_command": 4,
        "it_can_exist_without_parameters": False
    },
    {  # 56
        "id": 56,
        "id_device": 7,
        "id_command": 29,
        "it_can_exist_without_parameters": False
    },
    {  # 57
        "id": 57,
        "id_device": 7,
        "id_command": 30,
        "it_can_exist_without_parameters": False
    },
    {  # 58
        "id": 58,
        "id_device": 8,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {  # 59
        "id": 59,
        "id_device": 8,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {  # 60
        "id": 60,
        "id_device": 8,
        "id_command": 31,
        "it_can_exist_without_parameters": True
    },
    {  # 61
        "id": 61,
        "id_device": 8,
        "id_command": 32,
        "it_can_exist_without_parameters": True
    },
    {  # 62
        "id": 62,
        "id_device": 9,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {  # 63
        "id": 63,
        "id_device": 9,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    },
    {  # 64
        "id": 64,
        "id_device": 9,
        "id_command": 33,
        "it_can_exist_without_parameters": True
    },
    {  # 65
        "id": 65,
        "id_device": 9,
        "id_command": 29,
        "it_can_exist_without_parameters": False
    },
    {  # 66
        "id": 66,
        "id_device": 9,
        "id_command": 34,
        "it_can_exist_without_parameters": True
    },
    {  # 67
        "id": 67,
        "id_device": 9,
        "id_command": 35,
        "it_can_exist_without_parameters": True
    },
    {  # 68
        "id": 68,
        "id_device": 9,
        "id_command": 36,
        "it_can_exist_without_parameters": True
    },
    {  # 69
        "id": 69,
        "id_device": 9,
        "id_command": 37,
        "it_can_exist_without_parameters": True
    },
    {  # 70
        "id": 70,
        "id_device": 9,
        "id_command": 2,
        "it_can_exist_without_parameters": False
    },
    {  # 71
        "id": 71,
        "id_device": 9,
        "id_command": 3,
        "it_can_exist_without_parameters": False
    },
    {  # 72
        "id": 72,
        "id_device": 10,
        "id_command": 0,
        "it_can_exist_without_parameters": True
    },
    {  # 73
        "id": 73,
        "id_device": 10,
        "id_command": 1,
        "it_can_exist_without_parameters": True
    }
]
params = [
    {  # 0
        "name": "Яркость",
        "keywords": ["яркость", "свет", "освещение"],
        "is_required_name_param": True
    },
    {  # 1
        "name": "Цвет",
        "keywords": ["окраска", "свет", "освещение", "добавить яркость"],
        "is_required_name_param": False,
        "type": "String"
    },
    {  # 2
        "name": "Время",
        "keywords": ["период", "момент", "эпоха", "дата", "срок", "век", "эра",
                     "мгновение", "интервал", "отрезок", "таймер"],
        "is_required_name_param": False,
        "type": "Number"
    },
    {  # 3
        "name": "Громкость",
        "keywords": ["громкость", "громкость звука", "громкость сигнала", "уровень звука",
                     "громкость воспроизведения", "звук", "громкость звучания", "громкость музыки", "громкость голоса"],
        "is_required_name_param": True,
        "type": "Number"
    },
    {  # 4
        "name": "Плейлист",
        "keywords": ["список воспроизведения", "музыкальный список", "музыкальная подборка",
                     "подборка треков", "сет-лист", "перечень треков", "музыкальная коллекция"],
        "is_required_name_param": True,
        "type": "String"
    },
    {  # 5
        "name": "Альбом",
        "keywords": ["музыкальный альбом", "диск", "сборник", "пластинка", "релиз", "коллекция треков"],
        "is_required_name_param": True,
        "type": "String"
    },
    {  # 6
        "name": "Температура",
        "keywords": ["темп", "теплота", "градусы", "степень", "тепло", "холод", "теплота"],
        "is_required_name_param": False,
        "type": "Number"
    },
    {  # 7
        "name": "Режим",  # для холодильника экономичный режим  режим отпуска режим быстрого замораживания сухой режим
        # для стиралки "хлопок", "спорт", "быстро", "эко", "шерсть", "детская","деликатная", "интенсивная", "повседневная"
        # для камеры "запись", "ночной режим", "дневной режим", "слежение"
        # для розетки "энергосбережение", "десткий режим"
        "keywords": ["мод", "режим работы", "режим функционирования",
                     "режим использования", "режим эксплуатации"],
        "is_required_name_param": False,
        "type": "Enum"
    },
    {  # 8
        "name": "Канал",
        "keywords": ["телеканал", "программа", "частота", "станция", "вещательный канал"],
        "is_required_name_param": True
        "type": "String"
    },
    {  # 9
        "name": "Программа",
        "keywords": ["телепрограмма", "телешоу", "телевизионное шоу", "телепередача", "телевизионный контент"],
        "is_required_name_param": False,
        "type": "String"
    },
    {  # 10
        # Number
        "name": "Количество оборотов",
        "keywords": ["число оборотов", "частота вращения", "скорость вращения", "оборачиваемость", "оборотистость",
                     "оборот"],
        "is_required_name_param": True,
        "type": "Number"
    },
    {  # 11
        "name": "Конфорка",
        "keywords": ["плита", "варочная панель", "варочная поверхность", "кухонная плита", "газовая плита",
                     "электрическая плита"],
        "is_required_name_param": True,
        "type": "Enum"
    },
    {  # 12
        "name": "Направление",
        "keywords": ["курс", "путь", "сторона", "ориентир", "траектория", "вектор", "целеуказание", "указание",
                     "маршрут"],
        "is_required_name_param": False,
        "type": "Enum"
    },
    {  # 13
        "name": "Масштаб",
        "keywords": ["размер", "величина", "уровень", "степень", "мера", "охват", "размах", "пропорция", "диапазон"],
        "is_required_name_param": True,
        "type": "Number"
    },
]
type_value_param = [
    {  # 0
        "type": "Number",#TODO: Нужно научить определять в какую сторону (увечивать или уменьшать)
    },
    {  # 0
        "type": "String",
    },
    {  # 0
        "type": "Enum",#TODO: Должна быть привязка к устройству
    },
]
value_measurement_param = [
    {
        "id": 1,
        "measurement": "percent"
    },
    {
        "id": 2,
        "measurement": "hour"
    },
    {
        "id": 3,
        "measurement": "minute"
    },
    {
        "id": 4,
        "measurement": "second"
    },
    {
        "id": 5,
        "measurement": "day"
    },
    {
        "id": 6,
        "measurement": "week"
    },
    {
        "id": 7,
        "measurement": "month"
    },
    {
        "id": 8,
        "measurement": "year"
    },
    {
        "id": 9,
        "measurement": "hour"
    },
    {
        "id": 10,
        "measurement": "degree Celsius"
    },
    {
        "id": 11,
        "measurement": "degree Fahrenheit"
    },
    {
        "id": 12,
        "measurement": "kelvin"
    }
]
smart_devices_and_params_commands = [
    {
        "id_device_command": 2,
        "id_param": 0
    },
    {
        "id_device_command": 3,
        "id_param": 0
    },
    {
        "id_device_command": 0,
        "id_param": 2
    },
    {
        "id_device_command": 1,
        "id_param": 2
    },
    {
        "id_device_command": 4,
        "id_param": 1
    },
    {
        "id_device_command": 5,
        "id_param": 2
    },
    {
        "id_device_command": 6,
        "id_param": 2
    },
    {
        "id_device_command": 7,
        "id_param": 3
    },
    {
        "id_device_command": 8,
        "id_param": 3
    },
    {
        "id_device_command": 5,
        "id_param": 4
    },
    {
        "id_device_command": 5,
        "id_param": 5
    },
    {
        "id_device_command": 23,
        "id_param": 6
    },
    {
        "id_device_command": 24,
        "id_param": 6
    },
    {
        "id_device_command": 21,
        "id_param": 7
    },
    {
        "id_device_command": 29,
        "id_param": 3
    },
    {
        "id_device_command": 30,
        "id_param": 3
    },
    {
        "id_device_command": 31,
        "id_param": 8
    },
    {
        "id_device_command": 31,
        "id_param": 9
    },
    {
        "id_device_command": 36,
        "id_param": 7
    },
    {
        "id_device_command": 37,
        "id_param": 6
    },
    {
        "id_device_command": 38,
        "id_param": 6
    },
    {
        "id_device_command": 37,
        "id_param": 10
    },
    {
        "id_device_command": 38,
        "id_param": 10
    },
    {
        "id_device_command": 50,
        "id_param": 6
    },
    {
        "id_device_command": 51,
        "id_param": 0
    },
    {
        "id_device_command": 52,
        "id_param": 0
    },
    {
        "id_device_command": 53,
        "id_param": 2
    },
    {
        "id_device_command": 54,
        "id_param": 2
    },
    {
        "id_device_command": 55,
        "id_param": 1
    },
    {
        "id_device_command": 58,
        "id_param": 11
    },
    {
        "id_device_command": 59,
        "id_param": 11
    },
    {
        "id_device_command": 55,
        "id_param": 2
    },
    {
        "id_device_command": 62,
        "id_param": 7
    },
    {
        "id_device_command": 63,
        "id_param": 7
    },
    {
        "id_device_command": 65,
        "id_param": 12
    },
    {
        "id_device_command": 70,
        "id_param": 13
    },
    {
        "id_device_command": 71,
        "id_param": 13
    },
    {
        "id_device_command": 72,
        "id_param": 7
    },
    {
        "id_device_command": 73,
        "id_param": 7
    }

]
data = {'device': [],
        'command': [],
        'keywords': []}
result = {
    "query": [],
    "result": []
}

for i in range(0, len(devices)):
    local_smart_devices_and_commands = [item for item in smart_devices_and_commands if item["id_device"] == i]
    for local_smart_device_and_command in local_smart_devices_and_commands:
        print(f'Название устройства - {devices[i]["name"]} Название команды - {commands[local_smart_device_and_command["id_command"]]["command"]} id устройства - {i} id команды {local_smart_device_and_command["id_command"]}\n')
        # local_result = devices[i]["name"] + ", " + commands[local_smart_device_and_command["id_command"]]["command"]
        # local_query = [[f"{command} {device}", f"{device} {command}"]
        #                for command in commands[local_smart_device_and_command["id_command"]]["keywords"] for device in
        #                devices[i]["keywords"]]
        # local_query = list(set(list(chain.from_iterable(local_query))))
        # for j in range(0, len(local_query)): result["result"].append(local_result)
        # result["query"] += local_query


# pd.DataFrame(result).to_csv(Path.cwd().parent / Path("Data/smart_house_commands.csv"), encoding='utf-8',
#                             index=True, sep=';')
