import dateparser
from datetime import datetime, timedelta


class DateAndTime:
    def extract_and_convert_time(self, text: str) -> float:

        parsed_time = dateparser.parse(text, languages=['ru'], settings={'PREFER_DATES_FROM': 'future'})

        if parsed_time:
            # Приведение к стандартному типу datetime
            parsed_time = datetime(parsed_time.year, parsed_time.month, parsed_time.day,
                                   parsed_time.hour, parsed_time.minute, parsed_time.second)

            # Текущее время
            now = datetime.now()

            # Вывод отладочной информации
            print(f"Текущее время: {now}")
            print(f"Распознанное время: {parsed_time}")

            # Преобразование в секунды
            time_seconds = (parsed_time - now).total_seconds()

            # Проверка, если parsed_time в прошлом
            if time_seconds < 0:
                print("Распознанное время в прошлом или ошибочно в предыдущем месяце, исправляем.")
                # Проверка месяца и добавление месяца, если необходимо
                if parsed_time.month < now.month or (parsed_time.month == now.month and parsed_time.day < now.day):
                    # Увеличиваем месяц на 1
                    next_month = (parsed_time.month % 12) + 1
                    year_increment = parsed_time.month // 12
                    parsed_time = parsed_time.replace(month=next_month, year=parsed_time.year + year_increment)
                else:
                    # Добавление недели, если дата все еще в этом месяце, но прошлая
                    parsed_time += timedelta(weeks=1)

                # Повторное вычисление времени в секундах
                time_seconds = (parsed_time - now).total_seconds()
                print(f"Исправленное время: {parsed_time}")

            return time_seconds
        else:
            return None
