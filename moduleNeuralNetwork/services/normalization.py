from gensim.utils import simple_preprocess
from pymorphy3 import MorphAnalyzer


class Normalization:
    def normalize(self, raw_text: str) -> list:
        return self.__lemmatization(self.__tokenization(raw_text))

    def __tokenization(self, text: str) -> list:
        return simple_preprocess(text)

    def __lemmatization(self, tokens: list) -> list:
        lemmatizer = MorphAnalyzer()
        return list(lemmatizer.normal_forms(token)[0] for token in tokens)
