from flask import render_template, request, Blueprint
from apps.model.rabin_karp_similarity_model import CombinedRabinKarpDeepLearningModel, RabinKarpSimilarityModel

blueprint = Blueprint('analisis_blueprint', __name__)
@blueprint.route('/analisis', methods=['GET', 'POST'])
def analisis():
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        
        # Gabungkan judul dan abstrak dari input pengguna
        combined_user_doc = title + " " + abstract
        
        # Ambil data latih dari MySQL
        training_data = RabinKarpSimilarityModel().get_training_data()

        # Buat model gabungan Rabin-Karp dan Deep Learning
        model = CombinedRabinKarpDeepLearningModel()

        # Preprocessing data pelatihan untuk deep learning
        training_docs = [data['title'] + " " + data['abstract'] for data in training_data]
        padded_sequences, tokenizer = model.deep_learning_model.preprocess_data(training_docs)

        results = []
        for i, data in enumerate(training_data):
            combined_training_doc = data['title'] + " " + data['abstract']
            
            # Hitung similarity gabungan antara input pengguna dan data latih
            similarity = model.combined_similarity(combined_user_doc, combined_training_doc, tokenizer)
            
            # Bulatkan similarity ke 2 desimal
            similarity_percentage = round(similarity, 2)

            # Filter hasil berdasarkan similarity >= 50
            if similarity_percentage >= 50:
                results.append({
                    'title': data['title'],
                    'abstract': data['abstract'],
                    'similarity': similarity_percentage  # Tampilkan sebagai persentase bulat
                })
        
        # Tampilkan hasil analisis jika ada
        if results:
            return render_template('home/analisis.html', results=results, segment='analisis')
        else:
            return render_template('home/analisis.html', segment='analisis')

    # Render halaman analisis
    return render_template('home/analisis.html', segment='analisis')
