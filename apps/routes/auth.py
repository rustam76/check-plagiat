from flask import session, Blueprint, request, redirect, url_for, render_template
from apps.controller.auth_controller import AuthController
from flask_login import logout_user, login_required, login_user, current_user

blueprint = Blueprint('auth_blueprint',__name__)


@blueprint.route('/')
def default_route():
    return redirect(url_for('auth_blueprint.login'))

@blueprint.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        auth = AuthController()
        user =auth.login(username, password)
        if user:
            login_user(user)
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(url_for('home_blueprint.index'))
        else:
            # Stay on login page and show error message
            return render_template('accounts/login.html', msg="Invalid username or password.")
    
    return render_template('accounts/login.html')

@blueprint.route('/logout')
# @login_required
def logout():
    logout_user()
    return redirect(url_for('auth_blueprint.login'))



