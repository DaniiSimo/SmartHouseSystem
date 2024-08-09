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

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.label_encoder = LabelEncoder()

    def read_file(self, file_name: str) -> pd.DataFrame:
        df = pd.read_csv(file_name, encoding='utf-8')
        return df

    def train_model(self, df: pd.DataFrame, max_seq_length: int, embedding_dim: int, epochs: int,
                    batch_size: int) -> keras.Model:
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

        print(f"Точность: {accuracy:.2f}")

        return model

    def save_model(self, model) -> json:
        model_structure = model.to_json()
        with open('../data/lstm_model.json', 'w') as json_file:
            json_file.write(model_structure)

        model.save_weights('../data/lstm.weights.h5')

        with open('../data/tokenizer.pickle', 'wb') as handle:
            pickle.dump(self.tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('../data/label_encoder.pickle', 'wb') as handle:
            pickle.dump(self.label_encoder, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_model(self, struct_file: str, weight_file: str) -> keras.Model:
        with open(struct_file, 'r') as f:
            json_string = f.read()
        model = model_from_json(json_string)

        model.load_weights(weight_file)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        with open('../Command_handle/tokenizer.pickle', 'rb') as handle:
            self.tokenizer = pickle.load(handle)

        with open('../Command_handle/label_encoder.pickle', 'rb') as handle:
            self.label_encoder = pickle.load(handle)

        return model

    def predict_label(self, text: str, model: keras.Model, max_seq_length: int, file='../data/predicted_result.json') -> json:
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

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return file