import re

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
        """Menghitung tingkat similarity antara dua dokumen"""
        # Preprocessing dokumen
        doc1 = self.preprocess_text(doc1)
        doc2 = self.preprocess_text(doc2)
        
        # Membuat shingle
        shingles1 = self.k_gram_shingling(doc1)
        shingles2 = self.k_gram_shingling(doc2)
        
        # Menghitung hash untuk setiap shingle
        hash_set1 = set(self.rabin_karp_hash(shingle) for shingle in shingles1)
        hash_set2 = set(self.rabin_karp_hash(shingle) for shingle in shingles2)
        
        # Menghitung intersection dari hash set
        intersection = len(hash_set1 & hash_set2)
        
        # Menghitung Dice Similarity Coefficient
        dsc = (2 * intersection) / (len(hash_set1) + len(hash_set2)) * 100
        
        return dsc

    def compute_similarity_for_dataset(self, dataset):
        """Menghitung similarity untuk setiap pasangan dokumen dalam dataset"""
        similarities = {}
        n = len(dataset)
        for i in range(n):
            for j in range(i + 1, n):
                doc1, doc2 = dataset[i], dataset[j]
                title1, abstract1 = doc1['title'], doc1['abstract']
                title2, abstract2 = doc2['title'], doc2['abstract']
                
                # Gabungkan judul dan abstrak
                combined_doc1 = title1 + " " + abstract1
                combined_doc2 = title2 + " " + abstract2
                
                # Hitung similarity
                similarity = self.calculate_similarity(combined_doc1, combined_doc2)
                
                # Simpan hasil similarity
                similarities[(i, j)] = similarity
        
        return similarities

# Contoh Penggunaan
dataset = [
    {'title': 'Machine Learning in Healthcare', 'abstract': 'Machine learning techniques are revolutionizing healthcare.'},
    {'title': 'Applications of Machine Learning in Healthcare', 'abstract': 'The use of machine learning is growing in the healthcare industry.'},
    {'title': 'Deep Learning in Image Recognition', 'abstract': 'Deep learning techniques have achieved state-of-the-art results in image recognition.'},
]

# Inisialisasi model
model = RabinKarpSimilarityModel(k=4, prime=101)

# Menghitung similarity antara dokumen dalam dataset
similarities = model.compute_similarity_for_dataset(dataset)

# Menampilkan hasil similarity
for pair, similarity in similarities.items():
    print(f"Similarity between document {pair[0]} and document {pair[1]}: {similarity:.2f}%")
