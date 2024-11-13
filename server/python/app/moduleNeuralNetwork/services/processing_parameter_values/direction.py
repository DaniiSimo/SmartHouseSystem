import sys
import difflib
from number import Number

sys.path.insert(1, '../enums')
from operator_number import Operator_number
from unit_direction import UnitDirection

sys.path.insert(1, '..')
from normalization import Normalization


# Ключевое слово
class Direction:
    __default_value = 10  # TODO эксперементально подобрать
    __synonyms_direction = {
        'лево': ['влево', 'налево', 'левый'],
        'право': ['вправо', 'направо', 'правый'],
        'верх': ['наверх', 'вверх'],
        'низ': ['вниз'],
        'перед': ['впереди', 'спереди', 'вперёд'],
        'зад': ['сзади, позади', 'назад']
    }
    __synonyms_actions = {
        'повернуть': ['развернуть', 'вращать', 'крутить', 'завернуть', 'свернуть', 'изменять', 'направить',
                      'подвернуть', 'сместить', 'отклонять', 'отвернуть', 'переориентировать', 'перевернуть',
                      'вывернуть', 'обернуть', 'перестроить', 'уворачивать', 'закрутить', 'вывести', 'перенаправить',
                      'искривить', 'сбить', 'подвинуть'],
        'наклонить': ['склонить', 'наклонять', 'пригнуть', 'перегнуть', 'согнуть', 'отклонить', 'покосить', 'повалить',
                      'опустить', 'перекосить', 'нагнуть', 'сдвинуть', 'скосить', 'откинуть', 'завалить'],
    }
    __operations_direction = {
        'лево': {
            'повернуть': {
                'operator': Operator_number.DIFFERENCE,
                'direction': UnitDirection.YAW
            },
            'наклонить': {
                'operator': Operator_number.DIFFERENCE,
                'direction': UnitDirection.ROLL
            },
        },
        'право': {
            'повернуть': {
                'operator': Operator_number.SUM,
                'direction': UnitDirection.YAW
            },
            'наклонить': {
                'operator': Operator_number.SUM,
                'direction': UnitDirection.YAW
            },
        },
        'верх': {
            'повернуть': {
                'operator': Operator_number.SUM,
                'direction': UnitDirection.PITCH
            },
            'наклонить': {
                'operator': Operator_number.SUM,
                'direction': UnitDirection.PITCH
            },
        },
        'низ': {
            'повернуть': {
                'operator': Operator_number.DIFFERENCE,
                'direction': UnitDirection.PITCH
            },
            'наклонить': {
                'operator': Operator_number.DIFFERENCE,
                'direction': UnitDirection.PITCH
            },
        },
        'перед': {
            'повернуть': {
                'operator': Operator_number.DIFFERENCE,
                'direction': UnitDirection.PITCH
            },
            'наклонить': {
                'operator': Operator_number.DIFFERENCE,
                'direction': UnitDirection.PITCH
            },
        },
        'зад': {
            'повернуть': {
                'operator': Operator_number.SUM,
                'direction': UnitDirection.PITCH
            },
            'наклонить': {
                'operator': Operator_number.SUM,
                'direction': UnitDirection.PITCH
            },
        },
    }

    def __init__(self, command: str):
        self.__command = command

    def convert_query(self, text_query: str):
        service_normalization = Normalization()
        service_number = Number()
        processed_query = service_normalization.lemmatization_query(
            service_number.convert_string_number(text=text_query))

    def __operation_extraction(self, split_text: list) -> list:
        operations = []
        local_operation = {}
        local_key_word = None
        for i in range(0, len(split_text)):
            word = split_text[i]
            word_is_float = word.replace('.', '', 1).isdigit()

            if not word_is_float:
                key_word = self.__check_occurrence_with_percentage(search_word=word,
                                                                   words=Direction.__synonym_words.values())
                if key_word:
                    self.__add_in_operations(operation=local_operation, operations=operations)
                    local_operation = {}
                    local_key_word = Number.__key_words[key_word]
                    continue

            # region Условия для добавления оператора
            if not word_is_float and word in local_key_word:
                self.__add_in_operations(operation=local_operation, operations=operations)
                local_operation = {
                    'operator': local_key_word[word]
                }
            if 'operator' not in local_operation and '' in local_key_word:
                local_operation['operator'] = local_key_word['']
            # endregion

            # region Условия определения процентное число или нет
            if (
                    not word_is_float
                    and 'operator' in local_operation
                    and self.__check_occurrence_with_percentage(search_word=word,
                                                                words=Number.__key_words_in_percent.values())
            ):
                local_operation['is_percent'] = True
            # endregion

            # region Условия определения значения операции
            if word_is_float and 'operator' in local_operation:
                local_operation['value'] = word
            # endregion

            if i == len(split_text) - 1:
                self.__add_in_operations(operation=local_operation, operations=operations)

        return operations

    def __check_occurrence_with_percentage(self, search_word: str, words: list) -> str | bool:
        """
        Приватный метод проверки соотвествия в процентном отношении слова
        Args:
            search_word (str): Проверяемое слово
            words (list): Слова
        Returns:
            str | bool: В случае если искомое слово совпадает с одним словом из списка на 85 процентов, тогда возвращает оно, иначе False
        """
        for word in words:
            if (difflib.SequenceMatcher(None, search_word, word).ratio() * 100) > 85:
                return word
        return False

    def __generate_lambda_expression(self, operations: list):
        for operation in operations:
            if operation['is_percent']:
                str_operations = f"({str_operations}) * "
            else:
                str_operations += f" {operation['operator'].value} {operation['value']}"

        return eval(f"lambda (yaw,pitch,roll): {str_operations}")


# Начальные углы ориентации камеры (в градусах)
yaw = 0  # Поворот вокруг оси Z (влево вправо)
pitch = 0  # Поворот вокруг оси Y (вверх вниз)
roll = 0  # Поворот вокруг оси X (вперёд назад)

# Изменения углов ориентации камеры (в градусах)
delta_yaw = 1  # Изменение угла yaw
delta_pitch = 0.5  # Изменение угла pitch
delta_roll = 0.1  # Изменение угла roll

# Обновление ориентации камеры в цикле
for step in range(100):  # Пример: 100 шагов движения камеры
    # Обновление углов ориентации камеры
    yaw += delta_yaw
    pitch += delta_pitch
    roll += delta_roll

    # Проверка на переполнение углов
    yaw = yaw % 360
    pitch = pitch % 360
    roll = roll % 360

    print(f"Шаг {step + 1}:")
    print(f"Новые углы ориентации камеры: yaw={yaw}, pitch={pitch}, roll={roll}")

func = lambda x, y, z: (x + 1, y + 1, z + 1)
print(func(4, 4, 4))
