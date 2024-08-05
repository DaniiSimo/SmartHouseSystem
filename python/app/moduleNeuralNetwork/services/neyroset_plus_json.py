import keras
import numpy as np
import pandas as pd
import nltk
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pymorphy3
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, SpatialDropout1D, Flatten
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import model_from_json

nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))
morph = pymorphy3.MorphAnalyzer()

class Neyroset:

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.label_encoder = LabelEncoder()

    def read_file(self, file_name: str) -> pd.DataFrame:
        df = pd.read_csv(file_name, encoding='utf-8', sep=';')
        return df

    def preprocess_text(self, text: str) -> str:
        tokens = word_tokenize(text.lower())
        tokens = [morph.parse(word)[0].normal_form for word in tokens if word.isalnum() and word not in stop_words]
        return ' '.join(tokens)

    def add_preprocess_text_column(self, df: pd.DataFrame) -> pd.DataFrame:
        df['processed_text'] = df['query'].apply(self.preprocess_text)
        return df

    def train_model(self, df: pd.DataFrame, max_seq_length: int, embedding_dim: int, epochs: int,
                    batch_size: int) -> keras.Model:
        self.tokenizer.fit_on_texts(df['processed_text'])
        sequences = self.tokenizer.texts_to_sequences(df['processed_text'])
        word_index = self.tokenizer.word_index

        X = pad_sequences(sequences, maxlen=max_seq_length)

        y = self.label_encoder.fit_transform(df['result'])
        y = to_categorical(y)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        callback = keras.callbacks.EarlyStopping(monitor='accuracy', patience=6)

        model = Sequential()
        model.add(Embedding(len(word_index) + 1, embedding_dim, input_length=max_seq_length))
        model.add(SpatialDropout1D(0.2))
        model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
        model.add(Flatten())
        model.add(Dense(y.shape[1], activation='softmax'))

        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test),
                  callbacks=[callback],
                  verbose=2)

        loss, accuracy = model.evaluate(X_test, y_test)
        print(f'Accuracy: {accuracy:.2f}')
        return model

    def save_model(self, model) -> json:
        model_structure = model.to_json()
        with open('lstm_model.json', 'w') as json_file:
            json_file.write(model_structure)

        model.save_weights('lstm.weights.h5')
        np.save('label_classes.npy', self.label_encoder.classes_)

    def load_model(self, struct_file: str, weight_file: str) -> keras.Model:
        with open(struct_file, 'r') as f:
            json_string = f.read()
        model = model_from_json(json_string)

        model.load_weights(weight_file)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.label_encoder.classes_ = np.load('label_classes.npy', allow_pickle=True)
        return model

    def predict_lable(self, text: str, model: keras.Model, max_seq_length: int, file='predicted_result.json') -> json:
        new_text_preprocessed = self.preprocess_text(text)
        new_sequence = self.tokenizer.texts_to_sequences([new_text_preprocessed])
        new_sequence_padded = pad_sequences(new_sequence, maxlen=max_seq_length)
        predicted_result = model.predict(new_sequence_padded)
        predicted_label = self.label_encoder.inverse_transform(np.argmax(predicted_result, axis=1))[0]
        split_predicted_lable = predicted_label.split(',')
        result = {
            'input_text': text,
            'predicted_label':
                {
                    'device': split_predicted_lable[0],
                    'action': split_predicted_lable[1]

                }
        }

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return file