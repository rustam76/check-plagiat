# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flaskext.mysql import MySQL
from importlib import import_module

from markupsafe import Markup 

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
from apps.routes import home, documents, analisis,auth, profile


@app.template_filter('truncate')
def truncate_filter(s, length=50):
    if len(s) > length:
        return Markup(f"{s[:length]}...")
    return s

# app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(auth.blueprint)
app.register_blueprint(home.blueprint)
app.register_blueprint(documents.blueprint)
app.register_blueprint(analisis.blueprint)
app.register_blueprint(profile.blueprint)



    

