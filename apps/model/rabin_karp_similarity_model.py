import re
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import numpy as np 
from apps.config import get_db_connection

class RabinKarpSimilarityModel:
    def __init__(self, k=4, prime=101):
        self.k = k  # Panjang K-gram
        self.prime = prime  # Nilai prima untuk hashing

    def preprocess_text(self, text):
        """Preprocess text dengan mengubah menjadi lowercase dan menghapus tanda baca"""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        return text

    def k_gram_shingling(self, text):
        """Membuat K-gram shingle dari teks"""
        return [text[i:i+self.k] for i in range(len(text) - self.k + 1)]

    def rabin_karp_hash(self, shingle):
        """Menghitung hash dari sebuah shingle menggunakan Rabin-Karp"""
        h = 0
        d = 256  # Jumlah karakter dalam alfabet (ASCII)
        for char in shingle:
            h = (d * h + ord(char)) % self.prime
        return h

    def calculate_similarity_with_training_data(self, doc1, doc2):
        """
        Menghitung tingkat similarity antara gabungan doc1 dan doc2
        dengan data training yang diambil dari database.
        """
        # Preprocessing dan penggabungan
        combined_doc = self.preprocess_text(doc1) + " " + self.preprocess_text(doc2)

        # Buat shingle dan hash untuk dokumen gabungan
        combined_shingles = self.k_gram_shingling(combined_doc)
        combined_hash_set = set(self.rabin_karp_hash(shingle) for shingle in combined_shingles)

        # Ambil data training
        training_data = self.get_training_data()

        # Hasil similarity dengan setiap dokumen dalam training data
        similarity_results = []
        for data in training_data:
            # Gabungkan dan preprocess data training
            training_doc = self.preprocess_text(data['judul_plagiarisme']) + " " + self.preprocess_text(data['abstrak_plagiarisme'])

            # Buat shingle dan hash untuk dokumen training
            training_shingles = self.k_gram_shingling(training_doc)
            training_hash_set = set(self.rabin_karp_hash(shingle) for shingle in training_shingles)

            # Hitung similarity
            intersection = len(combined_hash_set & training_hash_set)
            similarity = round((2 * intersection) / (len(combined_hash_set) + len(training_hash_set)) * 100)

            # Simpan hasil
            similarity_results.append({
                "training_title": data['judul_plagiarisme'],
                "training_abstract": data['abstrak_plagiarisme'],
                "similarity": similarity
            })

        # Urutkan hasil berdasarkan similarity tertinggi
        similarity_results.sort(key=lambda x: x['similarity'], reverse=True)

        return similarity_results

    @staticmethod
    def get_training_data():
        """Mengambil data dari database."""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT judul_plagiarisme, abstrak_plagiarisme FROM documents")
        training_data = cursor.fetchall()
        connection.close()
        return training_data

class DeepLearningModel:
    def __init__(self, model_path, tokenizer):
        self.model = load_model(model_path ,  compile=False)
        self.tokenizer = tokenizer

    def preprocess_data(self, texts):
        """Preprocessing data untuk digunakan dalam model deep learning"""
        processed_data = self.tokenizer.texts_to_sequences(texts)
        processed_data = pad_sequences(processed_data, maxlen=256)  # Pastikan panjang maksimal sesuai dengan model
        return processed_data

    def predict_similarity(self, doc1, doc2):
        """Menggunakan model untuk memprediksi similarity."""
        texts = [doc1, doc2]
        processed_data = self.preprocess_data(texts)
        predictions = self.model.predict(processed_data)
        return predictions[0]

class SimilarityCombiner:
    @staticmethod
    def combine_results(doc1, doc2, rabin_karp_model, dl_model):
        """Menggabungkan hasil dari Rabin-Karp dan model deep learning dalam bentuk persen"""
        # Hasil Rabin-Karp
        rabin_karp_results = rabin_karp_model.calculate_similarity_with_training_data(doc1, doc2)

        # Hasil Model Deep Learning
        dl_score = dl_model.predict_similarity(doc1, doc2)
        if isinstance(dl_score, np.ndarray):  # Periksa apakah dl_score adalah array numpy
            dl_score = float(dl_score.item())  # Konversi menjadi float jika hanya ada satu nilai

        # Gabungkan skor
        combined_score = (dl_score + rabin_karp_results[0]['similarity']) / 2 if rabin_karp_results else dl_score
        
        # Terapkan batas maksimal 25% untuk hasil plagiarisme
        max_plagiarism_threshold = 25
        plagiarism_score = min(round(combined_score * 100, 2), max_plagiarism_threshold)
        
        # Hitung persentase teks identik (dari Rabin-Karp)
        identical_text_percent = min(rabin_karp_results[0]['similarity'], max_plagiarism_threshold)
        
        # Hitung persentase kemiripan semantik (dari Deep Learning)
        semantic_similarity_percent = min(round(dl_score * 100), max_plagiarism_threshold)

        # Get the most similar training document for text display
        most_similar_doc = rabin_karp_results[0] if rabin_karp_results else None
        
        result = {
            "plagiarism_score": plagiarism_score,
            "identical_text_percent": identical_text_percent,
            "semantic_similarity_percent": semantic_similarity_percent,
            "rabin_karp_similarity": "Plagiarized" if rabin_karp_results[0]['similarity'] > 50 else "Original",
            "rabin_karp_similarity_score_percent": rabin_karp_results[0]['similarity'],
            "dl_similarity_score_percent": round(dl_score * 100),
            "combined_score_percent": round(combined_score * 100, 2),
            "verdict": "Plagiarized" if dl_score > 0.5 else "Original",
            "similar_text_title": most_similar_doc['training_title'] if most_similar_doc else "",
            "similar_text_abstract": most_similar_doc['training_abstract'] if most_similar_doc else "",
            "similarity_percentage": most_similar_doc['similarity'] if most_similar_doc else 0
        }

        return result
