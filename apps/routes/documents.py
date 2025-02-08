from flask import Blueprint, render_template, request, redirect, url_for
from apps.controller.documents_controller import DocumentsController 
from werkzeug.utils import secure_filename
import pandas as pd
import os
from flask_login import login_required, current_user


blueprint = Blueprint('documents_blueprint', __name__)


docum = DocumentsController()


ITEMS_PER_PAGE = 10

@blueprint.route('/documents', methods=['GET', 'POST'])
@login_required
def documents():
    if request.method == 'POST':

        if 'file' in request.files:
            file = request.files['file'] 
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join('uploads', filename)
                file.save(file_path)

                docum.create_data_bulk(file_path)

                return redirect(url_for('documents_blueprint.documents'))
            
        else:    
            title = request.form['title']
            abstract = request.form['abstract']
            docum.create_data(title, abstract)

        return redirect(url_for('documents_blueprint.documents'))

    # Data simulasi yang akan dikirimkan ke template HTML
    page = request.args.get('page', 1, type=int)
    dataa = docum.get_data(page, ITEMS_PER_PAGE)
    return render_template('home/documents.html', segment='documents', data=dataa, page=page, ITEMS_PER_PAGE=ITEMS_PER_PAGE)


@blueprint.route('/documents/edit', methods=['POST'])
def edit_document():
    document_id = request.form['id']
    title = request.form['title']
    abstract = request.form['abstract']

    # Buat instance dari DocumentsController
    docum_controller = DocumentsController()
    
    # Panggil metode update_data pada instance
    docum_controller.update_data(document_id, title, abstract)
    
    return redirect(url_for('documents_blueprint.documents', page=1))


@blueprint.route('/documents/delete', methods=['POST'])
def delete_document():
    document_id = request.form['id']
    
    # Buat instance dari DocumentsController
    docum_controller = DocumentsController()
    
    # Panggil metode delete_data pada instance
    success = docum_controller.delete_data(document_id)
    
    if success:
        return redirect(url_for('documents_blueprint.documents', page=1))
    else:
        return "Failed to delete document", 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_file(file_path):
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    else:
        data = pd.read_excel(file_path)

    # Mengembalikan data sebagai list of dictionaries
    return data.to_dict(orient='records')