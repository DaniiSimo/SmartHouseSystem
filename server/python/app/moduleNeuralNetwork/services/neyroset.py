import keras
import numpy as np
import pandas as pd
import nltk
import json
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Dropout, Flatten
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import model_from_json
import pickle


class Neyroset:
    """
    Класс для создания нейросети

    Args:
        tokenizer (tensorflow.tokenizer): токенизирует предложения
        label_encoder (sklearn.LabelEncoder): преобразует слова в числовой вектор
    """

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.label_encoder = LabelEncoder()

    def read_file(self, file_name: str) -> pd.DataFrame:
        """
        Читает файл в формате csv

        Args:
            file_name (str): название файла

        Returns:
            df: датафрейм пандас
        """
        df = pd.read_csv(file_name, encoding='utf-8')
        return df

    def train_model(self, df: pd.DataFrame, max_seq_length: int = 20,
                    embedding_dim: int = 100,
                    epochs: int = 5,
                    batch_size: int = 16) -> keras.Model:
        """
        Запускает тренировку модели

        Args:
            df (pd.DataFrame): название датассета на котором будет происходить обучение
            max_seq_length (int): максимальный размер предложений
            embedding_dim (int): отвечает за размерность вектора
            epochs (int): устанавливает количество эпох обучения
            batch_size (int): задает размер тренировочных экземпляров прежде чем
                              начнется обратное распространение ошибки

        Returns:
            model: обученая модель keras
        """
        self.tokenizer.fit_on_texts(df['query'])
        sequences = self.tokenizer.texts_to_sequences(df['query'])
        word_index = self.tokenizer.word_index

        X = pad_sequences(sequences, maxlen=max_seq_length)

        y = self.label_encoder.fit_transform(df['result'])
        y = to_categorical(y)

        indices = np.arange(X.shape[0])
        np.random.shuffle(indices)
        X = X[indices]
        y = y[indices]

        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

        model = Sequential()
        model.add(Embedding(len(word_index) + 1, embedding_dim, input_length=max_seq_length))
        model.add(Dropout(0.2))
        model.add(LSTM(30, return_sequences=True))
        model.add(Flatten())
        model.add(Dense(y.shape[1], activation='softmax'))

        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
                  validation_data=(X_val, y_val), verbose=2)

        y_pred = model.predict(X_test)
        y_pred_labels = np.argmax(y_pred, axis=1)
        y_test_labels = np.argmax(y_test, axis=1)

        precision = precision_score(y_test_labels, y_pred_labels, average='weighted')
        recall = recall_score(y_test_labels, y_pred_labels, average='weighted')

        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")

        loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

        print(f"Accuracy: {accuracy:.2f}")

        return model

    def save_model(self, model) -> json:
        """
        Сохраняет модель, её веса, токенайзер и энкодер

        Args:
            model (tensorflow.keras): обученная модель

        Returns:
            сохраненные файлы
        """
        model_structure = model.to_json()
        with open('../data/lstm_model.json', 'w') as json_file:
            json_file.write(model_structure)

        model.save_weights('../data/lstm.weights.h5')

        with open('../data/tokenizer.pickle', 'wb') as handle:
            pickle.dump(self.tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('../data/label_encoder.pickle', 'wb') as handle:
            pickle.dump(self.label_encoder, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_model(self, struct_file: str, weight_file: str) -> keras.Model:
        """
        Загружает структуру модели, её веса, токенайзер и энкодер

        Args:
            struct_file (str): название файла структуры модели
            weight_file (str): название файла весов модели

        Returns:
            model: обученая модель keras
        """
        with open(struct_file, 'r') as f:
            json_string = f.read()
        model = model_from_json(json_string)

        model.load_weights(weight_file)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        with open('../data/tokenizer.pickle', 'rb') as handle:
            self.tokenizer = pickle.load(handle)

        with open('../data/label_encoder.pickle', 'rb') as handle:
            self.label_encoder = pickle.load(handle)

        return model

    def predict_label(self, text: str, model: keras.Model, max_seq_length: int = 20) -> json:
        """
        Предсказание метки класса переданой команды

        Args:
            text (str): запрос на естественном языке
            model (keras): обученая модель
            max_seq_length (int): максимальная длина предложения


        Returns:
            result: результат предсказания в формате json
        """
        new_sequence = self.tokenizer.texts_to_sequences([text])
        new_sequence_padded = pad_sequences(new_sequence, maxlen=max_seq_length)
        predicted_result = model.predict(new_sequence_padded)
        predicted_label = self.label_encoder.inverse_transform(np.argmax(predicted_result, axis=1))[0]
        split_predicted_label = predicted_label.split(',')
        result = {
            'input_text': text,
            'predicted_label':
                {
                    'device': split_predicted_label[0],
                    'action': split_predicted_label[1]
                }
        }

        return result

    def get_alternative_prediction(self, model, previous_label: str, text: str, max_seq_length: int = 20) -> dict:
        """
        Ищет альтернативное предсказание, если предыдущее было неверным, исключая предыдущую метку.
        """
        print(f"Исключаем метку: {previous_label}")

        previous_label_idx = np.where(self.label_encoder.classes_ == previous_label)[0]

        new_sequence = self.tokenizer.texts_to_sequences([text])
        new_sequence_padded = pad_sequences(new_sequence, maxlen=max_seq_length)

        predicted_result = model.predict(new_sequence_padded)

        if previous_label_idx.size > 0:
            predicted_result[0][previous_label_idx] = 0

        predicted_label = self.label_encoder.inverse_transform(np.argmax(predicted_result, axis=1))[0]

        split_alternative_label = predicted_label.split(',')
        result = {
            'input_text': text,
            'predicted_label': {
                'device': split_alternative_label[0],
                'action': split_alternative_label[1]
            }
        }

        return result

    def save_new_data(self, text: str, label: str):
        """
        Сохраняет новый пример для последующего обучения в формате CSV.

        Args:
            text (str): команда от пользователя
            label (str): метка класса для команды
        """
        file_path = '../data/false_predictions.csv'
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                pass
        except FileNotFoundError:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['query', 'result'])

        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([text.lower(), label])

    def funi_tune_model(self, new_data_path: str, old_data_path: str, max_seq_length: int = 20,
                           embedding_dim: int = 100, epochs: int = 5, batch_size: int = 16) -> keras.Model:
        """
        Метод для полного обучения модели на объединенных данных (старые + новые), используя существующий метод train_model.

        Args:
            new_data_path (str): путь к файлу с новыми данными (CSV)
            old_data_path (str): путь к файлу со старыми данными (CSV)
            max_seq_length (int): максимальная длина последовательности
            embedding_dim (int): размер векторных представлений слов
            epochs (int): количество эпох обучения
            batch_size (int): размер батча для обучения

        Returns:
            model: заново обученная модель
        """
        # Загружаем новые и старые данные
        new_data = self.read_file(new_data_path)
        old_data = self.read_file(old_data_path)

        # Объединяем новые и старые данные
        combined_data = pd.concat([old_data, new_data], ignore_index=True)

        # Запускаем обучение модели на объединенном наборе данных
        model = self.train_model(combined_data, max_seq_length=max_seq_length,
                                 embedding_dim=embedding_dim, epochs=epochs, batch_size=batch_size)

        return model
