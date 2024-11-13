import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from tensorflow.keras.preprocessing.sequence import pad_sequences
from python.app.moduleNeuralNetwork.services.neyroset import Neyroset
import matplotlib.pyplot as plt
import seaborn as sns
import datetime


class ModelAnalysis:
    """
    Класс анализа работоспсобности нейросети и датасета

    Args:
        model (tensorflow.keras): обученая модель
        tokenizer (tensorflow.tokenizer): токенизирует предложения
        label_encoder (sklearn.LabelEncoder): преобразует слова в числовой вектор
        max_seq_length (int): максимальная длина предложения
    """

    def __init__(self, model, tokenizer, label_encoder, max_seq_length=20):
        self.model = model
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder
        self.max_seq_length = max_seq_length

    def get_information(self, file_name: str):
        """
        Предоставляет информацию о датасете

        Args:
            file_name (str): название файла

        """
        df = pd.read_csv(file_name, encoding='utf-8', sep=';')
        classes_count = df['result'].value_counts().count()
        df['index'] = df['index'].astype('int16')
        print("Информация о датасете" + datetime.datetime.now().strftime('%Y-%m-%d') + ":")
        print(df.info())
        print(f"Количество классов: {classes_count}")

    def evaluate_model(self, file_name: str, num_classes: int = 10) -> pd.DataFrame:
        """
        Проверяет работоспособность оценивая нейросеть по трем мерам: precission, recall, F1

        Args:
            file_name (str): название файла
            num_classes (int): количество классов для анализа
        Returns:
            pd.DataFrame: датафрейм с результатами проверок

        """

        df = pd.read_csv(file_name, encoding='utf-8', sep=";")
        sequences = self.tokenizer.texts_to_sequences(df['query'])
        sequences_padded = pad_sequences(sequences, maxlen=self.max_seq_length)

        predicted_results = self.model.predict(sequences_padded)
        predicted_labels = np.argmax(predicted_results, axis=1)
        true_labels = self.label_encoder.transform(df['result'])

        unique_classes = np.unique(true_labels)

        if len(unique_classes) > num_classes:
            unique_classes = unique_classes[:num_classes]

        results = []
        for class_label in unique_classes:
            precision = precision_score(true_labels, predicted_labels, labels=[class_label], average='weighted',
                                        zero_division=0)
            recall = recall_score(true_labels, predicted_labels, labels=[class_label], average='weighted',
                                  zero_division=0)
            f1 = f1_score(true_labels, predicted_labels, labels=[class_label], average='weighted', zero_division=0)
            results.append({
                'Class': self.label_encoder.inverse_transform([class_label])[0],
                'Precision': precision,
                'Recall': recall,
                'F1-score': f1
            })

        results_df = pd.DataFrame(results)

        results_df.to_csv(
            '../analytics/analys_information/matrixscore-' + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv',
            index=False)

        return results_df

    def plot_class_distribution(self, df: pd.DataFrame):
        """
        Строит график распределения классов

        Args:
            pd.DataFrame: датасет для анализа

        """

        plt.figure(figsize=(14, 10))
        class_counts = df['result'].value_counts()
        sns.barplot(y=class_counts.index, x=class_counts.values, palette='viridis')
        plt.title('Распределение классов')
        plt.xlabel('Количество примеров')
        plt.ylabel('Класс')

        plt.yticks(fontsize=10, rotation=0, ha='right')
        plt.tight_layout()
        plt.show()

    def plot_evaluation_metrics(self, results_df: pd.DataFrame):
        """
        Строит график результатов оценки мерой F1

        Args:
            pd.DataFrame: датасет для анализа

        """

        plt.figure(figsize=(14, 8))
        sns.barplot(x='F1-score', y='Class', data=results_df.sort_values(by='F1-score', ascending=False),
                    palette='viridis')
        plt.title('F1-score для каждого класса')
        plt.xlabel('F1-score')
        plt.ylabel('Класс')
        plt.show()