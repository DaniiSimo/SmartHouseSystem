import sys
import os
import json
import difflib

sys.path.insert(1, '../enums')
from format_color import Format_color


class Color:
    """Сервис, переводящий строковое представление цвета в форматы RGB HEX CMYK HSV"""

    def parse(self, value: str, result_format: Format_color) -> str:
        """
        Публичный метод парсинга строкового значения цвета
        Args:
            value (str): Строковое название цвета
            result_format (Format_color): Формат в который надо перевести значение цвета

        Returns:
            str: Преобразованный цвет
        """
        like = 0
        code = None
        name = value.lower().strip()

        path_colors = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data',
                                   'data_parse_color_ru.json')
        colors = {}

        if os.path.exists(path_colors):
            with open(path_colors, 'r', encoding='utf-8') as file:
                colors = json.load(file)

        if colors and name:
            for code_, code_name in colors.items():
                if type(code_name) is str:
                    code_name = [code_name]

                for name_ in code_name:
                    name_ = name_.lower()
                    similarity = difflib.SequenceMatcher(None, name, name_).ratio() * 100
                    if similarity > 60.0 and similarity > like:
                        like = similarity
                        code = code_
        print(code)
        return self.__convert_color(int(code, 16), result_format)

    def __convert_color(self, value: int, result_format: Format_color, raw: bool = False) -> str:
        """
        Приватный метод преобразования числового значения 16-ой системы счисления в указанный формат
        Args:
            value (int): Числовое значение цвета в 16-ой системе счисления
            result_format (Format_color): Формат в который надо перевести значение цвета
            raw: bool: Возврат значения в виде строки или массива значений

        Returns:
            str: Преобразованный цвет
        """
        result = None

        if value is None:
            if result_format == Format_color.RGB:
                result = 'rgb(0,0,0)'
            elif result_format == Format_color.HEX:
                result = '#000000'
            elif result_format == Format_color.CMYK:
                result = 'cmyk(0,0,0,0)'
            elif result_format == Format_color.HSV:
                result = 'hsv(0,0,0)'
            return result

        pattern = None

        if value is not None:
            if result_format == Format_color.RGB:
                result = [
                    (value >> 16) & 0xFF,
                    (value >> 8) & 0xFF,
                    value & 0xFF
                ]
                pattern = 'rgb({},{},{})'

            elif result_format == Format_color.HEX:
                result = '#{:06X}'.format(value)

            elif result_format == Format_color.CMYK:
                r = (value >> 16) & 0xFF
                g = (value >> 8) & 0xFF
                b = value & 0xFF
                c_ = 1.0 - (r / 255)
                m_ = 1.0 - (g / 255)
                y_ = 1.0 - (b / 255)
                black = min(c_, m_, y_)
                cyan = (c_ - black) / (1.0 - black) if black != 1 else 0
                magenta = (m_ - black) / (1.0 - black) if black != 1 else 0
                yellow = (y_ - black) / (1.0 - black) if black != 1 else 0
                pattern = 'cmyk({:.2f},{:.2f},{:.2f},{:.2f})'
                result = [cyan, magenta, yellow, black]

            elif result_format == Format_color.HSV:
                r = (value >> 16) & 0xFF
                g = (value >> 8) & 0xFF
                b = value & 0xFF
                rgb_max = max(r, g, b)
                hsv = {'hue': 0, 'sat': 0, 'val': rgb_max}
                if hsv['val'] > 0:
                    r /= hsv['val']
                    g /= hsv['val']
                    b /= hsv['val']
                    rgb_min = min(r, g, b)
                    rgb_max = max(r, g, b)
                    hsv['sat'] = rgb_max - rgb_min
                    if hsv['sat'] > 0:
                        r = (r - rgb_min) / (rgb_max - rgb_min)
                        g = (g - rgb_min) / (rgb_max - rgb_min)
                        b = (b - rgb_min) / (rgb_max - rgb_min)
                        rgb_max = max(r, g, b)
                        if rgb_max == r:
                            hsv['hue'] = 0.0 + 60.0 * (g - b)
                            if hsv['hue'] < 0.0:
                                hsv['hue'] += 360.0
                        elif rgb_max == g:
                            hsv['hue'] = 120.0 + 60.0 * (b - r)
                        else:
                            hsv['hue'] = 240.0 + 60.0 * (r - g)
                pattern = 'hsv({},{},{})'
                result = [int(hsv['hue']), int(hsv['sat'] * 100), int(hsv['val'] * 100 / 255)]

            if not raw and pattern:
                result = pattern.format(*result)

            return result


serviceColor = Color()
print(serviceColor.parse('Красный', Format_color.HEX))
