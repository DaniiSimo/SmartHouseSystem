import sys
from words2numsrus import NumberExtractor

sys.path.insert(1, '../enums')
from operator_number import Operator_number

sys.path.insert(1, '..')
from normalization import Normalization


class Number:
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
    __key_words_in_percent = ['процент', '%']

    def convert_query(self, text_query: str):
        service_normalization = Normalization()
        processed_query = service_normalization.lemmatization_query(self.__convert_string_number(text_query))
        result_operations = []
        local_operation = {}
        local_key_word = None
        for word in processed_query:
            if word in Number.__key_words:
                if local_operation:
                    if 'operator' in local_operation and 'value' in local_operation:
                        local_operation['is_percent'] = local_operation['is_percent'] if 'is_percent' in local_operation else False
                        result_operations.append(local_operation)
                    local_operation = {}
                local_key_word = Number.__key_words[word]
                continue

            word_is_float = word.replace('.', '', 1).isdigit()

            #region Условия для добавления оператора
            if not word_is_float and word in local_key_word:
                if 'operator' in local_operation:
                    if 'value' in local_operation:
                        local_operation['is_percent'] = local_operation['is_percent'] if 'is_percent' in local_operation else False
                        result_operations.append(local_operation)
                    local_operation = {}
                local_operation['operator'] = local_key_word[word]
                continue
            if '' in local_key_word and 'operator' not in local_operation:
                local_operation['operator'] = local_key_word['']
            #endregion

            # region Условия определения процентное число или нет
            if (not word_is_float and 'operator' in local_operation
                    and word in Number.__key_words_in_percent):
                local_operation['is_percent'] = True
                continue
            # endregion

            # region Условия определения значения операции
            if word_is_float and 'operator' in local_operation:
                local_operation['value'] = word
                continue
            # endregion
        return result_operations

    def __convert_string_number(self, text: str) -> str:
        extractor = NumberExtractor()
        return extractor.replace_groups(text)

    def __operations_extraction(self, text: str) -> list:
        pass

    def __generate_lambda_expression(self, operations: list):
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
# func = number.generate_lambda_expression(operations=[
#     {'operator': Operator_number.SUM, 'value': '50', 'is_percent': True},
#     {'operator': Operator_number.DIFFERENCE, 'value': '30', 'is_percent': True},
#     {'operator': Operator_number.DIVIDING, 'value': '5', 'is_percent': False},
#     {'operator': Operator_number.ASSIGN, 'value': '50', 'is_percent': True},
# ])
print(number.convert_query('Прибавь 30 процентов уменьши на сто в двадцать два раза'))

# 'Увеличить' 'на' -> +x 'в' -> *x
# 'Уменьшить' 'на' -> -x 'в' -> /x
# 'Поставить' 'на' -> =x
