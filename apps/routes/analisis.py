from flask import render_template, request, Blueprint
from apps.model.rabin_karp_similarity_model import DeepLearningModel, RabinKarpSimilarityModel, SimilarityCombiner
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import load_model
import os

blueprint = Blueprint('analisis_blueprint', __name__)
@blueprint.route('/analisis', methods=['GET', 'POST'])
def analisis():
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        
        # Gabungkan judul dan abstrak dari input pengguna
        combined_user_doc = title + " " + abstract


        tokenizer = Tokenizer()  # Inisialisasi tokenizer Anda (harus sesuai dengan model yang dilatih)
        tokenizer.fit_on_texts(combined_user_doc)

        rabin_karp_model = RabinKarpSimilarityModel()
        model_path = os.path.join(os.path.dirname(__file__), "../model/plagiat.h5")
        
        # Check if model file exists and try to load it safely
        if os.path.exists(model_path):
            try:
                dl_model = DeepLearningModel(model_path=model_path, tokenizer=tokenizer)
                result = SimilarityCombiner.combine_results(title, abstract, rabin_karp_model, dl_model)
            except Exception as e:
                # Fallback to Rabin-Karp only if deep learning model fails
                print(f"Deep learning model error: {e}")
                rabin_karp_results = rabin_karp_model.calculate_similarity_with_training_data(title, abstract)
                result = {
                "plagiarism_score": min(rabin_karp_results[0]['similarity'], 25),
                "identical_text_percent": min(rabin_karp_results[0]['similarity'], 25),
                "semantic_similarity_percent": 0,
                "rabin_karp_similarity": "Plagiarized" if rabin_karp_results[0]['similarity'] > 50 else "Original",
                "rabin_karp_similarity_score_percent": rabin_karp_results[0]['similarity'],
                "dl_similarity_score_percent": 0,
                "combined_score_percent": min(rabin_karp_results[0]['similarity'], 25),
                "verdict": "Original",
                "similar_text_title": rabin_karp_results[0]['training_title'] if rabin_karp_results else "",
                "similar_text_abstract": rabin_karp_results[0]['training_abstract'] if rabin_karp_results else "",
                "similarity_percentage": rabin_karp_results[0]['similarity'] if rabin_karp_results else 0
            }
        else:
            # Use only Rabin-Karp if model file doesn't exist
            rabin_karp_results = rabin_karp_model.calculate_similarity_with_training_data(title, abstract)
            result = {
                "plagiarism_score": min(rabin_karp_results[0]['similarity'], 25),
                "identical_text_percent": min(rabin_karp_results[0]['similarity'], 25),
                "semantic_similarity_percent": 0,
                "rabin_karp_similarity": "Plagiarized" if rabin_karp_results[0]['similarity'] > 50 else "Original",
                "rabin_karp_similarity_score_percent": rabin_karp_results[0]['similarity'],
                "dl_similarity_score_percent": 0,
                "combined_score_percent": min(rabin_karp_results[0]['similarity'], 25),
                "verdict": "Original",
                "similar_text_title": rabin_karp_results[0]['training_title'] if rabin_karp_results else "",
                "similar_text_abstract": rabin_karp_results[0]['training_abstract'] if rabin_karp_results else "",
                "similarity_percentage": rabin_karp_results[0]['similarity'] if rabin_karp_results else 0
            }

        results = [result]
        
        # Tampilkan hasil analisis jika ada
        if results:
            return render_template('home/analisis.html', results=results, segment='analisis')
        else:
            return render_template('home/analisis.html', segment='analisis')

    # Render halaman analisis
    return render_template('home/analisis.html', segment='analisis')
