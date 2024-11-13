import dateparser
from python.app.moduleNeuralNetwork.services.processing_parameter_values.datetime import datetime, timedelta


class DateAndTime:
    def extract_and_convert_time(self, text: str) -> float:
        """
        Извлечение даты и время из запроса на ествественном языке

        Args:
            text (str): запрос на естественном языке

        Returns:
            time_seconds: значение преданного времени в секундах
        """
        parsed_time = dateparser.parse(text, languages=['ru'], settings={'PREFER_DATES_FROM': 'future'})

        if parsed_time:
            parsed_time = datetime(parsed_time.year, parsed_time.month, parsed_time.day,
                                   parsed_time.hour, parsed_time.minute, parsed_time.second)

            now = datetime.now()

            time_seconds = (parsed_time - now).total_seconds()

            if time_seconds < 0:

                if parsed_time.month < now.month or (parsed_time.month == now.month and parsed_time.day < now.day):
                    next_month = (parsed_time.month % 12) + 1
                    year_increment = parsed_time.month // 12
                    parsed_time = parsed_time.replace(month=next_month, year=parsed_time.year + year_increment)
                else:

                    parsed_time += timedelta(weeks=1)

                time_seconds = (parsed_time - now).total_seconds()

            return time_seconds
        else:
            return None
