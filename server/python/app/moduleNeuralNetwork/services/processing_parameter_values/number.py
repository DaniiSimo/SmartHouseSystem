import sys
from words2numsrus import NumberExtractor
import difflib

sys.path.insert(1, '../enums')
from operator_number import Operator_number

sys.path.insert(1, '..')
from normalization import Normalization

#TODO Ввести дефолтные значения для каждого парметра они разные

class Number:
    """Сервис, переводящий строковое представление числа в лямбда выражение"""
    __key_words = {
        'нарастить': {
            'на': Operator_number.SUM,
            'в': Operator_number.MULTIPLICATION
        },
        'увеличить': {
            'на': Operator_number.SUM,
            'в': Operator_number.MULTIPLICATION
        },
        'добавить': {
            '': Operator_number.SUM,
        },
        'прибавить': {
            '': Operator_number.SUM,
        },
        'снизить': {
            'на': Operator_number.DIFFERENCE,
            'в': Operator_number.DIVIDING
        },
        'сократить': {
            'на': Operator_number.DIFFERENCE,
            'в': Operator_number.DIVIDING
        },
        'убавить': {
            'на': Operator_number.DIFFERENCE,
            'в': Operator_number.DIVIDING
        },
        'уменьшить': {
            'на': Operator_number.DIFFERENCE,
            'в': Operator_number.DIVIDING
        },
        'перемножить': {
            '': Operator_number.MULTIPLICATION
        },
        'помножить': {
            '': Operator_number.MULTIPLICATION
        },
        'приумножить': {
            '': Operator_number.MULTIPLICATION
        },
        'разделить': {
            '': Operator_number.DIVIDING
        },
        'поделить': {
            '': Operator_number.DIVIDING
        },
        'расчленить': {
            '': Operator_number.DIVIDING
        },
        'поставить': {
            '': Operator_number.ASSIGN,
            'на': Operator_number.ASSIGN
        },
        'назначить': {
            '': Operator_number.ASSIGN,
            'на': Operator_number.ASSIGN
        },
        'присвоить': {
            '': Operator_number.ASSIGN
        },
        'уподобить': {
            '': Operator_number.ASSIGN
        },
        'отождествить': {
            '': Operator_number.ASSIGN
        },
    }
    "Ключевые слова для операций"
    __key_words_in_percent = ['процент', '%']
    "Ключевые слова для процента"

    def convert_query(self, text_query: str):
        """
        Публичный метод перевода строки в лямбда выражение
        Args:
            text_query (str): Необработанный текстовый запрос

        Returns:
            lambda: Выражение, полученное из строкового запроса
        """
        service_normalization = Normalization()
        processed_query = service_normalization.lemmatization_query(self.convert_string_number(text_query))
        operations = self.__operations_extraction(split_text=processed_query)
        return self.__generate_lambda_expression(operations=operations)

    def convert_string_number(self, text: str) -> str:
        """
        Приватный метод конвертации строкового представления числа в числовой вид
        Args:
            text (str): Необработанный текстовый запрос

        Returns:
            str: Текстовый запрос с числами
        """
        extractor = NumberExtractor()
        return extractor.replace_groups(text)

    def __operations_extraction(self, split_text: list) -> list:
        """
        Приватный метод выделения числовых операций из частей текста
        Args:
            split_text (list): Части текстового запроса

        Returns:
            list: Список операций
        """
        operations = []
        local_operation = {}
        local_key_word = None
        for i in range(0, len(split_text)):
            word = split_text[i]
            word_is_float = word.replace('.', '', 1).isdigit()

            if not word_is_float:
                key_word = self.__check_occurrence_with_percentage(search_word=word, words=Number.__key_words.keys())
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
                    and self.__check_occurrence_with_percentage(search_word=word, words=Number.__key_words_in_percent)
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

    def __add_in_operations(self, operation: dict, operations: list) -> None:
        """
        Приватный метод добавление операции в список операций
        Args:
            operation (dict): Добавляемая операция
            operations (list): Список операций
        Returns:
            None:
        """
        if 'operator' in operation and 'value' in operation:
            operation['is_percent'] = operation['is_percent'] if 'is_percent' in operation else False
            operations.append(operation)

    def __generate_lambda_expression(self, operations: list):
        """
        Приватный метод генерации лямбда выражений на основе операций
        Args:
            operations (list): Список операций
        Returns:
            lambda: Выражение, полученное из списка операций
        """
        index = -1
        for i, item in enumerate(operations):
            if item['operator'] == Operator_number.ASSIGN and not item['is_percent']:
                index = i

        start_value = ''
        if index == -1:
            start_value = 'x'
        else:
            operations = operations[index:]
            start_value = operations.pop(0)['value']

        str_operations = f'{start_value} '
        for operation in operations:
            if operation['is_percent']:
                str_operations = f"({str_operations}) * "
                match operation['operator']:
                    case Operator_number.SUM | Operator_number.MULTIPLICATION:
                        str_operations += f"{1 + float(operation['value']) / 100}"
                    case Operator_number.ASSIGN | Operator_number.DIFFERENCE | Operator_number.DIVIDING:
                        str_operations += f"{float(operation['value']) / 100}"
            else:
                str_operations += f" {operation['operator'].value} {operation['value']}"

        return eval(f"lambda x: {str_operations}")


number = Number()

print(number.convert_query('присвой 80 Прeбавь 20 пожалуйста працентов назначь 30  увеличь на 100')(100))

