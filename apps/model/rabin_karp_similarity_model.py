import re
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Embedding, LSTM, GlobalMaxPooling1D
from tensorflow.keras.models import Model
import numpy as np
from apps.config import get_db_connection

class RabinKarpSimilarityModel:
    def __init__(self, k=4, prime=101):
        self.k = k  # Panjang K-gram
        self.prime = prime  # Nilai prima untuk hashing
    
    def preprocess_text(self, text):
        """Preprocess text dengan mengubah menjadi lowercase dan menghapus tanda baca"""
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        return text

    def k_gram_shingling(self, text):
        """Membuat K-gram shingle dari teks"""
        shingles = []
        for i in range(len(text) - self.k + 1):
            shingles.append(text[i:i+self.k])
        return shingles

    def rabin_karp_hash(self, shingle):
        """Menghitung hash dari sebuah shingle menggunakan Rabin-Karp"""
        h = 0
        d = 256  # Jumlah karakter dalam alfabet (ASCII)
        for char in shingle:
            h = (d * h + ord(char)) % self.prime
        return h

    def calculate_similarity(self, doc1, doc2):
        """Menghitung tingkat similarity antara dua dokumen menggunakan Rabin-Karp"""
        doc1 = self.preprocess_text(doc1)
        doc2 = self.preprocess_text(doc2)

        shingles1 = self.k_gram_shingling(doc1)
        shingles2 = self.k_gram_shingling(doc2)

        hash_set1 = set(self.rabin_karp_hash(shingle) for shingle in shingles1)
        hash_set2 = set(self.rabin_karp_hash(shingle) for shingle in shingles2)

        intersection = len(hash_set1 & hash_set2)

        dsc = round((2 * intersection) / (len(hash_set1) + len(hash_set2)) * 100)
        return dsc
    
    @staticmethod
    def get_training_data():
        """Mengambil data dari database."""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT title, abstract FROM documents")
        training_data = cursor.fetchall()
        connection.close()
        return training_data

class DeepLearningModel:
    def __init__(self, vocab_size=20000, embedding_dim=128, lstm_units=64):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.model = self.build_model()

    def build_model(self):
        """Membangun arsitektur model deep learning menggunakan LSTM."""
        input_text = Input(shape=(None,), name='input_text')
        x = Embedding(self.vocab_size, self.embedding_dim)(input_text)
        x = LSTM(self.lstm_units, return_sequences=True)(x)
        x = GlobalMaxPooling1D()(x)
        x = Dense(64, activation='relu')(x)
        output = Dense(1, activation='sigmoid')(x)
        model = Model(inputs=input_text, outputs=output)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def preprocess_data(self, texts):
        """Preprocessing data untuk digunakan dalam model deep learning"""
        tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self.vocab_size)
        tokenizer.fit_on_texts(texts)
        sequences = tokenizer.texts_to_sequences(texts)
        padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(sequences, padding='post')
        return padded_sequences, tokenizer

    def predict_similarity(self, doc1, doc2, tokenizer):
        """Menggunakan model untuk memprediksi similarity."""
        sequences = tokenizer.texts_to_sequences([doc1, doc2])
        padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(sequences, padding='post')
        predictions = self.model.predict(padded_sequences)
        return predictions[0][0]

class CombinedRabinKarpDeepLearningModel:
    def __init__(self):
        self.rabin_karp_model = RabinKarpSimilarityModel()
        self.deep_learning_model = DeepLearningModel()

    def combined_similarity(self, doc1, doc2, tokenizer):
        """Menggabungkan similarity literal (Rabin-Karp) dan deep learning"""
        # Menghitung similarity literal dengan Rabin-Karp
        literal_similarity = self.rabin_karp_model.calculate_similarity(doc1, doc2)

        # Menghitung similarity semantik dengan deep learning
        semantic_similarity = self.deep_learning_model.predict_similarity(doc1, doc2, tokenizer)

        # Menggabungkan hasil similarity
        combined_score = (literal_similarity + semantic_similarity * 100) / 2
        return combined_score

# Contoh penggunaan


