from gensim.utils import simple_preprocess
from pymorphy3 import MorphAnalyzer
from nltk.tokenize import sent_tokenize
import spacy
import re
import subprocess
import sys
from nltk.tokenize import word_tokenize


# TODO Посмотреть где очищаются числа и исправить это
class Normalization:
    """Сервис, выполняющий предобработку текстового запроса пользователя"""

    def __init__(self):
        """
        Инициализация объекта и проверка установлен ли дамп, если нет установливаем через терминал
        """
        # try:
        #     spacy.load('ru_core_news_sm')
        # except OSError as e:
        #     subprocess.run([sys.executable, '-m', 'spacy', 'download', 'ru_core_news_sm'], check=True)

    def normalize(self, raw_text: str) -> list:
        """
        Публичный метод нормализации текстового запроса
        Args:
            raw_text (str): Необработанный текстовый запрос

        Returns:
            list: Обработанный запрос, разделённый на простые запросы
        """
        text = self.__translation_to_lower_case(text=raw_text)
        parts_text = self.__split_text(text=text)
        return [
            " ".join(
                self.__lemmatization(tokens=
                                     self.__tokenization(text=
                                                         self.__clean_text(text=part_text)
                                                         )
                                     )
            )
            for part_text in parts_text
        ]

    def lemmatization_query(self, raw_text: str) -> str:
        return self.__lemmatization(self.__tokenization(raw_text))

    def __tokenization(self, text: str) -> list:
        """
        Приватный метод токенизации текстового запроса
        Args:
            text (str): Предъобработанный текстовый запрос

        Returns:
            list: Список токенов
        """
        return word_tokenize(text, language="russian")
        return simple_preprocess(text, min_len=1)

    def __split_text(self, text: str) -> list:
        """
        Разбиение сложного текстового запроса на простые
        Args:
            text (str): Сложный текстовый запрос

        Returns:
            list: Список простых запросов
        """
        pattern_split_text = r'\b(?:и|да|тоже|также|а|ни|или|либо|зато|однако|затем|,|;)\b'
        result = []
        for sentence in sent_tokenize(text, language="russian"):
            result += [part.strip() for part in re.split(pattern_split_text, sentence) if part.strip()]
        return result

    def __lemmatization(self, tokens: list) -> list:
        """
        Леммитизация токенов
        Args:
            tokens (list): Список токенов

        Returns:
            list: Список леммитизированных токенов
        """
        lemmatizer = MorphAnalyzer()
        return [lemmatizer.normal_forms(token)[0] for token in tokens]

    def __translation_to_lower_case(self, text: str) -> str:
        """
        Перевод текстового запроса в нижний регистр
        Args:
            text (str): Необработанный текст

        Returns:
            str: Текст в нижнем регистре
        """
        return text.lower()

    def __clean_text(self, text: str) -> str:
        """
        Очистка текста от стоп слов
        Args:
            text (str): Необработанный текст

        Returns:
            str: Очищенный текст
        """
        nlp = spacy.load('ru_core_news_sm')
        doc = nlp(text)
        return ' '.join([token.text for token in doc if not token.is_stop])


print(Normalization().normalize(
    raw_text='вперед'))
