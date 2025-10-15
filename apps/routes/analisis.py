from flask import render_template, request, Blueprint, jsonify
from apps.model.rabin_karp_similarity_model import FinalModel, SimilarityCombiner
import os

blueprint = Blueprint('analisis_blueprint', __name__)
@blueprint.route('/analisis', methods=['GET','POST'])
def analisis():
    if request.method == 'POST':
        title1 = request.form.get('title', '')
        abstract1 = request.form.get('abstract', '')
        title2 = request.form.get('title', '')
        abstract2 = request.form.get('abstract', '')

        if not title1 or not abstract1 or not title2 or not abstract2:
            return jsonify({'error': 'Title dan Abstract dari kedua dokumen harus diisi'}), 400
        
        try:
            final_model = FinalModel()
            results = SimilarityCombiner.combine_results(
                title1, abstract1, title2, abstract2, final_model
            )
            return jsonify(results)
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return jsonify({'error': str(e)}), 500

    return render_template('home/analisis.html')


