import itertools

import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from spacy.language import Language


class Classificator:
    def __init__(self):
        self.__nlp = spacy.load("ru_core_news_lg")
        self.__matcher = None

        @Language.component("custom_component")
        def custom_component(doc):
            lowercase_text = " ".join([token.lemma_.lower() for token in doc])

            with self.__nlp.disable_pipes("custom_component"):
                lowercase_doc = self.__nlp(lowercase_text)

            matches = self.__matcher(lowercase_doc)
            spans = []

            for match_id, start, end in matches:
                label = self.__nlp.vocab.strings[match_id]
                span = Span(doc, start, end, label=label)
                spans.append(span)

            # region Проверка на пересечения
            filtered_spans = []
            checking_span = None
            for i in range(0, len(spans)):
                if i == len(spans) - 1:
                    if checking_span is not None:
                        filtered_spans.append(checking_span)
                    else:
                        filtered_spans.append(spans[i])
                    break
                current_span = spans[i]
                next_span = spans[i + 1]
                if current_span.end < next_span.end:
                    if checking_span is not None:
                        filtered_spans.append(checking_span)
                        checking_span = None
                    else:
                        filtered_spans.append(current_span)
                else:
                    if checking_span is None:
                        checking_span = current_span
                    else:
                        checking_span = checking_span if len(checking_span) >= len(current_span) else current_span
            # endregion
            doc.ents = filtered_spans
            return doc

        self.__nlp.add_pipe("custom_component", last=True)

    def classification(self, text_query: str, data_match: dict, create_new_words: bool = False) -> list:
        self.__matcher = PhraseMatcher(self.__nlp.vocab)
        for key, key_words in data_match.items():
            if create_new_words:
                self.__matcher.add(key, self.__create_new_combination_words(words=key_words))
            else:
                self.__matcher.add(key, [self.__nlp.make_doc(key_word.lower()) for key_word in key_words])
        doc = self.__nlp(text_query)
        hard_ents = [{'token': ent.lemma_, 'type': ent.label_} for ent in doc.ents if len(ent) > 1]
        index_hard_ent = None
        result = []
        for token in doc:
            index_ent = next((i for i, value in enumerate(hard_ents) if token.text in value['token']), -1)
            if index_ent != -1:
                index_hard_ent = index_ent
                continue
            if index_hard_ent is not None:
                result.append(hard_ents[index_hard_ent])
                index_hard_ent = None
            result.append({"token": token.text, "type": token.ent_type_})
        if index_hard_ent is not None:
            result.append(hard_ents[index_hard_ent])
        return result

    def __create_new_combination_words(self, words: list) -> list:
        result = set()
        for word in words:
            parts_word = word.lower().strip().split()
            if not parts_word:
                continue
            if len(parts_word) > 1:
                for perm in itertools.permutations(parts_word):
                    result.add(self.__nlp.make_doc(' '.join(perm)))
            else:
                result.add(self.__nlp.make_doc(parts_word[0]))
        return list(result)
