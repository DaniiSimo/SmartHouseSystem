import spacy

# Загрузка модели spaCy
nlp = spacy.load("ru_core_news_sm")


class Temperature:

    def convert_to_celsius(self, value, unit) -> float:
        """Конвертирует температуру в Цельсий."""
        if unit in ['f', '°f', 'fahrenheit']:
            return (value - 32) * 5.0 / 9.0
        elif unit in ['k', 'kelvin', 'к', 'кельвин']:
            return value - 273.15
        else:
            return value

    def extract_and_convert_temperatures(self, text: str) -> list:
        """
        Возвращает преобразованную температуру в градусах цельсия

        """

        doc = nlp(text)
        temperatures = []

        for token in doc:
            # Проверка на числа
            if token.like_num:
                # Поиск следующего токена
                next_token = token.nbor()
                if next_token.text in ['°', 'градусов']:
                    next_token = next_token.nbor()
                # Поиск единиц измерения температуры
                if next_token.text.lower() in ['c.', '°c.', 'с', '°с', 'celsius', 'цельсий', 'цельсия',
                                               'f', '°f', 'f.', '°f.', 'фаренгейта', 'фаренгейт', 'fahrenheit',
                                               'k', '°k', 'k.', '°k.', 'kelvin', 'кельвин', 'кельвина']:
                    # Удаление знаков препинания
                    try:
                        value = float(token.text)
                        temp_celsius = self.convert_to_celsius(value, next_token.text.lower())
                        temperatures.append(f"{temp_celsius:.2f}")
                    except ValueError:
                        print(f"Невозможно преобразовать в число: {token.text}")

        return temperatures
