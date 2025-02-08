import hashlib
from flask import flash, request, session, Blueprint, render_template
from jinja2 import TemplateNotFound

from apps.model.auth_model import AuthModel
blueprint = Blueprint('profile_blueprint', __name__)
from flask_login import login_required


@blueprint.route('/profile', methods=['POST'])
@login_required 
def profile():
    
    current_username = request.form.get('username') 
    new_password = request.form.get('new_password')  
    auth = AuthModel()

    success = auth.update_user(current_username, new_username=current_username, new_password=new_password)

    if success:
        flash("Profile updated successfully!")
    else:
        flash("Failed to update profile. Please try again.")

    return render_template('home/index.html', segment='index', username=current_username)
    

