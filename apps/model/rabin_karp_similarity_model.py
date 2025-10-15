import re
import numpy as np 
from apps.config import get_db_connection
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, roc_curve, confusion_matrix
import joblib
import tensorflow as tf

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

class FinalModel:
    def __init__(self):
        # Load pre-trained Keras model directly
        self.model = None
        self.is_trained = False
        self.encoder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.load_keras_model()

    def load_keras_model(self):
        """Load pre-trained Keras model"""
        try:
            model_path = "e:/Flutter/saskia/check-plagiat/apps/model/plagiarism_model_keras.h5"
            self.model = tf.keras.models.load_model(model_path)
            self.is_trained = True
            print("✅ Model berhasil dimuat kembali.")
        except Exception as e:
            print(f"Error loading Keras model: {e}")
            self.is_trained = False

    def preprocess_data(self, doc1, doc2):
        """Gunakan format yang sama seperti saat training model"""
        emb1 = self.encoder.encode([doc1])[0]
        emb2 = self.encoder.encode([doc2])[0]

        # fitur sesuai training: absolute difference
        features = np.abs(emb1 - emb2).reshape(1, -1)
        return features

    def predict_similarity(self, doc1, doc2):
        """Prediksi similarity antar dua dokumen"""
        if not self.is_trained or self.model is None:
            raise ValueError("Model belum dimuat.")

        X_input = self.preprocess_data(doc1, doc2)
        y_pred_prob = self.model.predict(X_input)
        probability = float(y_pred_prob[0][0])
        y_pred = 1 if probability > 0.5 else 0

        return {
            'prediction': y_pred,
            'probability': probability,
            'similarity_score': probability * 100
        }


    def train_model(self, X_train, y_train):
        """Train model (not needed for pre-trained Keras model)"""
        print("Model sudah dilatih sebelumnya, tidak perlu training lagi")
        self.is_trained = True


    def save_model(self, filepath):
        """Save trained model"""
        if self.is_trained and self.model is not None:
            self.model.save(filepath)
        else:
            raise ValueError("Model belum dimuat. Tidak dapat disimpan.")

    def load_model(self, filepath):
        """Load trained model"""
        self.model = tf.keras.models.load_model(filepath)
        self.is_trained = True

class SimilarityCombiner:
    @staticmethod
    def combine_results(title1, abstract1, title2, abstract2, final_model):
        try:
            # Gabungkan masing-masing dokumen
            text1 = f"{title1} {abstract1}"
            text2 = f"{title2} {abstract2}"
            
            final_result = final_model.predict_similarity(text1, text2)
            final_score = final_result['similarity_score']
            
        except Exception as e:
            print(f"Error in final model: {e}")
            final_score = 0
        
        verdict = "Plagiarized" if final_score > 50 else "Original"
        
        return {
            "plagiarism_score": final_score,
            "semantic_similarity_percent": final_score,
            "dl_similarity_score_percent": final_score,
            "combined_score_percent": final_score,
            "rabin_karp_similarity": "Original",
            "rabin_karp_similarity_score_percent": 0,
            "verdict": verdict
        }
