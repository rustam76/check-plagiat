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
      
        dl_model = DeepLearningModel(model_path=model_path, tokenizer=tokenizer)

      

        result = SimilarityCombiner.combine_results(title, abstract, rabin_karp_model, dl_model)

        results = [result]
        
        # Tampilkan hasil analisis jika ada
        if results:
            return render_template('home/analisis.html', results=results, segment='analisis')
        else:
            return render_template('home/analisis.html', segment='analisis')

    # Render halaman analisis
    return render_template('home/analisis.html', segment='analisis')
