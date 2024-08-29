from apps.home import blueprint
from flask import render_template, request, redirect, url_for
from jinja2 import TemplateNotFound

from apps.model.documents import Document

docum = Document()

@blueprint.route('/')
# @login_required
def index():
    return render_template('home/index.html')



# Route untuk menampilkan data
@blueprint.route('/documents', methods=['GET', 'POST'])
def document():

    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        print(title, abstract)
        docum.create(title, abstract)

        return redirect(url_for('home_blueprint.documents'))

    # Data simulasi yang akan dikirimkan ke template HTML
    dataa = docum.get_documents_all()
    return render_template('home/documents.html', data=dataa)



@blueprint.route('/<template>')
# @login_required
def route_template(template):

    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None